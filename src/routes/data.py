from fastapi import APIRouter, Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers import Settings, get_settings
import os
from controllers import DataController,ProjectController
import aiofiles
from models import UserResponses


data_router=APIRouter(prefix="/api/v1/data", tags=["data"])

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    # Validate the file type
    is_valid,result_signal= DataController().validate(file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal":result_signal})

    project_dir_path = ProjectController().get_project_path(project_id)

    file_path= os.path.join(project_dir_path
                            ,file.filename)
    
    async with aiofiles.open(file_path ,"wb") as f:
        while chunk := await file.read(app_settings.File_Chunk_size):
            await f.write(chunk)

    return JSONResponse({"signal": UserResponses.FILE_UPLOAD_SUCCESS.value})





     