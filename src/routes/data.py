from fastapi import APIRouter, Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
import os
from controllers import DataController,ProjectController,Process_controller
import aiofiles
from models import UserResponses,Assets_Type
import logging
from .schemas.data import PROCESS_FILE
from models import Projects,ADD_Chunks,ASSETS
from models.schemas import Chunk,Asset
from tasks.processing import process_project_files
from tasks.process_workflow import process_and_push


logger = logging.getLogger('uvicorn.error')



data_router=APIRouter(prefix="/api/v1/data", tags=["data"])

@data_router.post("/upload/{project_id}")
async def upload_file(request : Request , project_id: int,file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    # Validate the file type
    is_valid,result_signal= DataController().validate(file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal":result_signal})




    # add project_id to the collection in Mongodb
    add_to_clientdb= await Projects.call_two_functions(clientdb=request.app.client_db)
    project= await add_to_clientdb.get_project_or_create_one(project_id=project_id)




    data_controller=DataController()
    file_path, file_id = data_controller.generate_unique_file_name(
        origin_file_name=file.filename,
        project_id=project_id
    )
    
    try:
        async with aiofiles.open(file_path ,"wb") as f:
            while chunk := await file.read(app_settings.File_Chunk_size):
                await f.write(chunk)
    
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": UserResponses.FILE_UPLOAD_FAILED.value
            }
        )
    
    # store assets in mongodb
    asset= await ASSETS.call_two_functions(clientdb=request.app.client_db)

    asset_resource=Asset(  
        Asset_project_id=project.project_id,
        Asset_name=file_id,
        Asset_size=os.path.getsize(file_path),
        Asset_type=Assets_Type.FILE.value
    )

    asset_record = await asset.create_asset(asset=asset_resource)

    return JSONResponse(
            content={
                "signal": UserResponses.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.Asset_name),
                "project_id":str(project.project_id)
            }
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id : int, processrequest: PROCESS_FILE):

    Chunk_size=processrequest.chunk_size
    Chunk_overlap=processrequest.chunk_overlap
    do_reset=processrequest.do_reset
    file_id = processrequest.file_id


    task=process_project_files.delay(project_id=project_id,
                                     file_id=file_id,
                                     chunk_size=Chunk_size,
                                     overlap_size=Chunk_overlap,
                                     do_reset=do_reset)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "signal":UserResponses.PROCESSING_SUCCESS.value,
            "task_id":task.id 
        }
    )



@data_router.post("/process_and_push/{project_id}")
async def process_and_push_endpoint(project_id:int,processrequest: PROCESS_FILE):
    

    Chunk_size=processrequest.chunk_size
    Chunk_overlap=processrequest.chunk_overlap
    do_reset=processrequest.do_reset
    file_id = processrequest.file_id


    workflow_task=process_and_push.delay(
       project_id=project_id
       ,file_id=file_id
       ,chunk_size=Chunk_size
       ,overlap_size=Chunk_overlap
       ,do_reset=do_reset
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "signal":"The task has been received",
            "task_id":workflow_task.id
        }
    )





            