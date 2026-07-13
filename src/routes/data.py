from fastapi import APIRouter, Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
import os
from controllers import DataController,ProjectController,Process_controller
import aiofiles
from models import UserResponses
import logging
from .schemas.data import PROCESS_FILE
from models import Projects

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
    
    add_to_clientdb= Projects(clientdb=request.app.client_db)
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
    return JSONResponse(
            content={
                "signal": UserResponses.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id,
                "project_id":str(project._id)
            }
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id : str, processrequest: PROCESS_FILE):

    file_id=processrequest.file_id
    Chunk_size=processrequest.chunk_size
    Chunk_overlap=processrequest.chunk_overlap

    ProcessController = Process_controller(project_id=project_id)

    file_content= ProcessController.get_file_content(file_id= file_id)

    file_chunks=ProcessController.process_file_content(file_content=file_content,chunk_overlap=Chunk_overlap,chunk_size=Chunk_size,file_id=file_id)


    if file_chunks is None or len(file_chunks)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal":UserResponses.PROCESSING_FAILED.value
                            })   
    return file_chunks




     