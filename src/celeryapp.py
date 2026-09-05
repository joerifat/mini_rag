from celery import Celery
from helpers.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.llm import LLMFactory,LLMFACTORY
from stores.VectorDB import VectorDbFactory
from stores.llm.templates.template_parser import TemplateParser



settings=get_settings()


async def setup_utils():
        
        Postgres_url=f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@pgvector:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
    
        db_engine=create_async_engine(Postgres_url)
        client_db=sessionmaker(
            db_engine,class_=AsyncSession,expire_on_commit=False
        )
    
    
        
    
        llm_provider_factory = LLMFactory(config=settings)
    
        #generation model
        generation_model= llm_provider_factory.create(provider=LLMFACTORY.OLLAMA.value)
        generation_model.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
        #Embedding model
        embedding_model=llm_provider_factory.create(provider=LLMFACTORY.OLLAMA.value)
        embedding_model.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
        #VectorDB
        vectordb=VectorDbFactory(settings,client_db= client_db)
        vectordb_provider=vectordb.createDB(provider=settings.VECTOR_DB_BACKEND)
        await  vectordb_provider.connect()
    
        #templateparser
        template_parser=TemplateParser(language=settings.PRIMARY_LANGUAGE,
                                           deafult_language=settings.DEAFULT_LANGUAGE)


        return (db_engine, client_db, llm_provider_factory, vectordb,
            generation_model, embedding_model,vectordb_provider, template_parser)
    
    



celery_app=Celery(
    "mini_rag",
    broker=settings.CELERY_RABBITMQ_URL,
    backend=settings.CELERY_RESULT_BACKEND_URL,
    include=[
        "tasks.processing",
        "tasks.indexing",
        "tasks.process_workflow"
    ]
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer= settings.CELERY_TASK_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_ignore_result=False,
    result_expires=3600,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,
    task_routes={
        "tasks.processing.process_project_files": {"queue": "file_processing"},
        "tasks.indexing.index_data": {"queue":"indexing_data"},
        "tasks.process_workflow.process_and_push": {"queue": "file_processing"},
    },
    control_queue_exclusive=True,
    control_queue_durable=False,
    event_queue_exclusive=True
)

celery_app.conf.task_default_queue = "default"

