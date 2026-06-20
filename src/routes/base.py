from fastapi import APIRouter
import os

base_router=APIRouter(
    prefix="/api/v1",
    tags=["base"]
)


@base_router.get("/")
def hello_world():
    return {"message": "Hello World!"}

@base_router.get("/env")
async def get_env_variable():
    App_name= os.getenv("APP_NAME")
    App_version= os.getenv("APP_VERSION")
    return {"app_name":App_name, "app_version":App_version}

