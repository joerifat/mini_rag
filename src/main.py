from fastapi import FastAPI
from routes import base_router,data_router,nlp_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
from stores.llm import LLMFactory,LLMFACTORY
from stores.VectorDB import VectorDbFactory
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)


app=FastAPI(lifespan=lifespan)


async def startup_db_client(app:FastAPI):
    settings= get_settings()


    app.mongo_connection= AsyncIOMotorClient(settings.MONGODB_URL)
    app.client_db= app.mongo_connection[settings.MONGODB_NAME]

    llm_provider_factory = LLMFactory(config=settings)

    #generation model
    app.generation_model= llm_provider_factory.create(provider=LLMFACTORY.OpenAi.value)
    app.generation_model.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    #Embedding model
    app.embedding_model=llm_provider_factory.create(provider=LLMFACTORY.COHERE.value)
    app.embedding_model.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #VectorDB
    vector_db_provider=VectorDbFactory(settings)
    app.Vectordb=vector_db_provider.createDB(provider=settings.VECTOR_DB_BACKEND)
    app.Vectordb.connect()



async def shutdown_db_client(app:FastAPI):
    app.mongo_connection.close()
    app.Vectordb.disconnect()




app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)


