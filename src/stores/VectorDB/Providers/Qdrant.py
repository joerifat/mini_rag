from qdrant_client import QdrantClient, models
from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnum import DistanceMethodEnums
from typing import List


class QdrantDB(VectorDBInterface):

    def __init__(self,db_path: str,distance_method:str):
        self.client=None
        self.db_path=db_path
        self.distance_method=None
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method=models.Distance.COSINE

        elif distance_method== DistanceMethodEnums.DOT.value:
            self.distance_method=models.Distance.DOT
        

        self.logger=logging.getLogger(__name__)

    def connect(self):
        self.client=QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client=None

    def is_collection_exit(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)


    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name):
        if self.is_collection_exit(collection_name=collection_name):
         return self.client.delete_collection(collection_name=collection_name)

        self.logger.error(f"No such collection with this name to delete or do_reset: {collection_name}")
        return None


    def create_collection(self, collection_name: str, embedding_size: int, do_rest: bool=False):

        if do_rest:
            _=self.delete_collection(collection_name=collection_name)

        if self.is_collection_exit(collection_name=collection_name):
            self.logger.error(f"The collection with name :{collection_name} is already exist")
            return False

        _=self.client.create_collection(collection_name=collection_name,
                                        vectors_config=models.VectorParams(size=embedding_size,
                                                                                distance=self.distance_method))
        self.logger.info(f"collection {collection_name} is created")
        return True


    def insert_one(self, collection_name:str, text:str, vector:list, metadata:dict = None, record_id:str = None):

        if not self.is_collection_exit(collection_name=collection_name):
            self.logger.error(f"This collection: {collection_name} is not exist")
            return False

        try:
            _=self.client.upload_records(collection_name=collection_name,
                                            records=[
                                                models.Record(
                                                    vector=vector,
                                                    payload={
                                                        "text":text,
                                                        "metadata":metadata
                                                    }
                                                )
                                            ])
        except Exception as e:
            self.logger.error(f"Error while inserting record {e}")

        return True


    def insert_many(self, collection_name:str, text: list, vector: list, metadata: list = None, record_id:list = None,batch_size: int=50):
        if not self.is_collection_exit(collection_name=collection_name):
            self.logger.error(f"This collection: {collection_name} is not exist")
            return False

        if metadata is None:
            metadata =len(text)*[None]

        if record_id is None:
            record_id= len(text)*[None]
        

        

        for i in range(0,len(text),batch_size):

            batch_end=i+batch_size

            batch_text=text[i:batch_end]
            batch_vector=vector[i:batch_end]
            batch_metadata=metadata[i:batch_end]
            batch_vector_id=record_id[i:batch_end]

            batch_records=[
                models.Record(
                    id=batch_vector_id[x],
                    vector=batch_vector[x],
                    payload={"text":batch_text[x],"metadata":batch_metadata[x]}
                )

                for x in range(len(batch_text))
            ]
            try:

                 _=self.client.upload_records(collection_name=collection_name,
                                         records=batch_records)
                 return True

            except Exception as e:
                self.logger.error(f"Error while inserting vectors {e}")
                return False

        return True

            

    def search_by_vector(self, collection_name, vector, limit):

        return self.client.search(collection_name=collection_name,
                                  query_vector=vector,
                                  limit=limit)



    

    
        




    



