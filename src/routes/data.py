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
from models.schemas import Chunks,Assets


logger = logging.getLogger('uvicorn.error')



data_router=APIRouter(prefix="/api/v1/data", tags=["data"])

@data_router.post("/upload/{project_id}")
async def upload_file(request : Request , project_id: str,file: UploadFile,
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

    asset_resource=Assets(  
        asset_project_id=project.id,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_type=Assets_Type.FILE.value
    )

    asset_record = await asset.create_asset(asset=asset_resource)

    return JSONResponse(
            content={
                "signal": UserResponses.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.asset_name),
                "project_id":str(project.id)
            }
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request ,project_id : str, processrequest: PROCESS_FILE):

    Chunk_size=processrequest.chunk_size
    Chunk_overlap=processrequest.chunk_overlap
    do_reset=processrequest.do_reset

    add_to_clientdb= await Projects.call_two_functions(clientdb=request.app.client_db)
    project= await add_to_clientdb.get_project_or_create_one(project_id=project_id)
    
    
    asset= await ASSETS.call_two_functions(clientdb=request.app.client_db)
    
    asset_project_id={}
    if processrequest.file_id:
        result= await asset.get_one_file(asset_project_id=project.id,asset_name=processrequest.file_id)
        if result is None:
            return JSONResponse(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 content={
                     "signal":UserResponses.FILE_ID_ERROR_VALUE.value
                 }
             )
        asset_project_id={
            result.id:result.asset_name
        }

    else:

        result= await asset.get_all_project_assets(asset_project_id=project.id,asset_type=Assets_Type.FILE)

        asset_project_id={
            rec.id : rec.asset_name
            for rec in result
        }

    if len(asset_project_id)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal":UserResponses.NO_FILES_ERROR.value}
            )
        
    ProcessController = Process_controller(project_id=project_id) 

    chunks = await ADD_Chunks.call_two_functions(clientdb=request.app.client_db)

    if do_reset == 1:
            _ = await chunks.delete_chunks_by_project_id(
                project_id=project.id
            ) 


    num_chunks=0
    no_files=0

    for id,file_id in asset_project_id.items():
                
        file_content= ProcessController.get_file_content(file_id= file_id)

        if file_content is None:
            logger.info(f"Error while processing file id {file_id}")
            continue

        file_chunks=ProcessController.process_file_content(file_content=file_content,chunk_overlap=Chunk_overlap,chunk_size=Chunk_size,file_id=file_id)


        if file_chunks is None or len(file_chunks)==0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "signal":UserResponses.PROCESSING_FAILED.value
                                })   
        
        file_chunks_SchemeObject=[
            Chunks(chunk_text=i.page_content,
                chunk_metadata=i.metadata,
                chunk_order=order+1,
                chunk_project_id=project.id,
                chunk_asset_id=id)
            for order,i in enumerate(file_chunks)
        ]

        num_chunks += await chunks.add_many_chunks(chunks=file_chunks_SchemeObject,batchsize=10)
        no_files+=1
            


    return JSONResponse(status_code=status.HTTP_202_ACCEPTED,
                        content={"signal":UserResponses.PROCESSING_SUCCESS.value,
                                "len_chun":num_chunks,
                                "processed_files":no_files})




            