from .base_controller import BaseController
from models.schemas import Chunks,Project
from stores.llm.llm_enums import CohertEnum
from helpers import get_settings
from typing import List



class NlpController(BaseController):
    def __init__(self,vectordb_client,embedding_model,generation_model,
                ):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.embedding_model=embedding_model
        self.settings=get_settings()
        self.generation_model=generation_model
        self.vectordb=vector_db


    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()


    def reset_vector_db_collection(self,project_id: str):
        collection_name=self.create_collection_name(project_id=project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self,project_id):
        collection_name=self.create_collection_name(project_id=project_id)
        return self.vectordb_client.get_collection_info(collection_name=collection_name)   



    def index_into_vectordb(self,project:Project,chunks:List[Chunks],chunks_ids: List[int] ,do_rest:bool = False):

        #step 1 get collection name
        collection_name=self.create_collection_name(project_id=project.project_id)

        #step 2 get chunks
        texts=[
            c.chunk_text
            for c in chunks
        ]
        metadata=[
            c.chunk_metadata
            for c in chunks
        ]

        vectors=[
            self.embedding_model.create_embeddings(text=text,document_type=CohertEnum.DOCUMENT.value
                                            )
            for text in texts
        ]

        #create collection if not exist

        self.vectordb_client.create_collection( collection_name=collection_name,
                                                embedding_size=self.settings.EMBEDDING_MODEL_SIZE,
                                                do_rest=do_rest)

        #insert into vector db

        _=self.vectordb_client.insert_many(collection_name=collection_name,
                                          text=texts,
                                          vector=vectors,
                                          metadata=metadata,
                                          record_id=chunks_ids)

        return True


    def search_by_vector(self,query:str,project:Project,limit:int =5):

        collection_name=self.create_collection_name(project_id=project.project_id)

        vector=self.embedding_model.create_embeddings(text=query, document_type=CohertEnum.QUERY.value)

        if not vector or len(vector) == 0:
            return False

        result=self.vectordb_client.search_by_vector(
             collection_name=collection_name, vector=vector, limit=limit

        )
        if not result:
            return False

        return True

        







    


    