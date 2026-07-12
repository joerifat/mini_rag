from fastapi import FastAPI
from routes import base_router,data_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings


app=FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings= get_settings()


    app.mongo_connection= AsyncIOMotorClient(settings.MONGODB_URL)
    app.client_db= app.mongo_connection(settings.MONGODB_NAME)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_connection.close()

app.include_router(base_router)
app.include_router(data_router)


