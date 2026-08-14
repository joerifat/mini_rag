from helpers import Settings
from .VectorDBEnum import DB
from .Providers import QdrantDB,PGVectorDB
from controllers import BaseController
from sqlalchemy.orm import sessionmaker



class VectorDbFactory:
    def __init__(self,config:Settings,client_db:sessionmaker=None):
        self.config = config
        self.client_db=client_db

    def createDB(self,provider: str):
        provider= provider.upper() if provider else ""

        if provider == DB.QDRANT.value:
            db_path=BaseController().get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDB(db_path=db_path,distance_method=self.config.DISTANCE_METHOD)

        elif provider== DB.PGVetor.value:

            return PGVectorDB(client_db=self.client_db,distance_method=self.config.DISTANCE_METHOD,
                              embedding_size=self.config.EMBEDDING_MODEL_SIZE,
                              indexing_method=self.config.INDEXING_METHOD,
                              )

        return None

