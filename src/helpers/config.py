from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str
    APP_version: str
    APP_description: str
    SECRET_KEY: str
    FILE_TYPE_AVAILABLE: list
    FILE_SIZE_LIMIT: int
    File_Chunk_size: int


    OPENAI_APIKEY:Optional[str]=None
    COHERE_APIKEY: Optional[str]=None
    OPENAi_URL: Optional[str]=None

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    INPUT_DAFAULT_MAX_CHARACTERS: int
    GENERATION_DAFAULT_MAX_TOKENS: int
    GENERATION_DAFAULT_TEMPERATURE: float

    DISTANCE_METHOD:str
    VECTOR_DB_BACKEND: str
    INDEXING_METHOD:str

    DEAFULT_LANGUAGE: str ="en"
    PRIMARY_LANGUAGE: str

    
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT : int
    POSTGRES_DATABASE: str
    BASE_URL:str
    
    class Config:
        env_file=".env"

def get_settings():
    return Settings()        