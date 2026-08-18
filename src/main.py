from fastapi import FastAPI
from routes import base_router,data_router,nlp_router
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from helpers import get_settings
from stores.llm import LLMFactory,LLMFACTORY
from stores.VectorDB import VectorDbFactory
from contextlib import asynccontextmanager
from stores.llm.templates.template_parser import TemplateParser
from utils.metrics import setup_metrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)


app=FastAPI(lifespan=lifespan)

setup_metrics(app)


async def startup_db_client(app:FastAPI):
    settings= get_settings()

    Postgres_url=f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@localhost:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"

    app.db_engine=create_async_engine(Postgres_url)
    app.client_db=sessionmaker(
        app.db_engine,class_=AsyncSession,expire_on_commit=False
    )


    

    llm_provider_factory = LLMFactory(config=settings)

    #generation model
    app.generation_model= llm_provider_factory.create(provider=LLMFACTORY.OLLAMA.value)
    app.generation_model.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    #Embedding model
    app.embedding_model=llm_provider_factory.create(provider=LLMFACTORY.OLLAMA.value)
    app.embedding_model.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #VectorDB
    vectordb=VectorDbFactory(settings,client_db=app.client_db)
    app.vectordb_provider=vectordb.createDB(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_provider.connect()

    #templateparser
    app.template_parser=TemplateParser(language=settings.PRIMARY_LANGUAGE,
                                       deafult_language=settings.DEAFULT_LANGUAGE)


async def shutdown_db_client(app:FastAPI):
    await app.db_engine.dispose()
    await app.Vectordb.disconnect()




app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)


