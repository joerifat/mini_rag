from fastapi import APIRouter,Depends
from helpers import get_settings,Settings

base_router=APIRouter(
    prefix="/api/v1",
    tags=["base"]
)


@base_router.get("/")
def hello_world():
    return {"message": "Hello World!"}

@base_router.get("/env")
async def get_env_variable(app_settings : Settings = Depends(get_settings)):
    App_name = app_settings.APP_NAME 
    App_version = app_settings.APP_version 
    return {"app_name": App_name, "app_version": App_version,"Owner":"Youssef_rifat"}
