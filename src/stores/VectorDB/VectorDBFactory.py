from helpers import Settings
from .VectorDBEnum import Qdrantdb
from .Providers import QdrantDB
from controllers import BaseController



class VectorDbFactory:
    def __init__(self,config:Settings):
        self.config = config

    def createDB(self , provider: str):
        provider= provider.upper() if provider else ""

        if provider == Qdrantdb.QDRANT.value:
            db_path=BaseController.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDB(db_path=db_path,distance_method=self.config.DISTANCE_METHOD)

