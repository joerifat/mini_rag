from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_version: str
    APP_description: str
    SECRET_KEY: str
    FILE_TYPE_AVAILABLE: list
    FILE_SIZE_LIMIT: int
    File_Chunk_size: int


    OPENAI_APIKEY: str
    COHERE_APIKEY: str
    OPENAi_URL: str

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
    VECTOR_DB_PATH: str

    DEAFULT_LANGUAGE: str ="en"
    PRIMARY_LANGUAGE: str

    
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT : int
    POSTGRES_DATABASE: str
    
    class Config:
        env_file=".env"

def get_settings():
    return Settings()        