from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_version: str
    APP_description: str
    SECRET_KEY: str
    FILE_TYPE_AVAILABLE: list
    FILE_SIZE_LIMIT: int
    File_Chunk_size: int
    MONGODB_URL: str
    MONGODB_NAME: str
    
    class Config:
        env_file=".env"

def get_settings():
    return Settings()        