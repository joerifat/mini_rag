from fastapi import APIRouter, Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
import os
from controllers import DataController,ProjectController
import aiofiles
from models import UserResponses
import logging


logger = logging.getLogger('uvicorn.error')



data_router=APIRouter(prefix="/api/v1/data", tags=["data"])

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    # Validate the file type
    is_valid,result_signal= DataController().validate(file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal":result_signal})
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
                "file_id": file_id
            }
        )





     