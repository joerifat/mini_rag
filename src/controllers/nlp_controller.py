from .base_controller import BaseController
from models.schemas import Chunk
from stores.llm.llm_enums import CohertEnum
from typing import List
import json


class NlpController(BaseController):
    def __init__(self,vector_db,generation_model,embedding_model,template_parser):
        self.vector_db=vector_db
        self.generation_model=generation_model
        self.embedding_model=embedding_model
        self.tempalte_parser=template_parser


    async def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()

    async def reset_vector_db_collection(self,project_id: str):
        collection_name= await self.create_collection_name(project_id=project_id)
        return self.vector_db.delete_collection(collection_name=collection_name)




    async def get_info_about_collection(self,project_id:str):
        collection_name=await self.create_collection_name(project_id=project_id)
        collection_info=self.vector_db.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )

    async def index_into_vector_db(self,project_id:str,chunks:List[Chunk],chunk_ids:List[int],do_rest:bool=False):

        collection_name=await self.create_collection_name(project_id=project_id)

        text=[
            c.chunk_text
            for c in chunks
        ]

        metadata=[
            c.chunk_metadata
            for c in chunks
        ]

        vectors=[
            self.embedding_model.create_embeddings(text=c,document_type=CohertEnum.DOCUMENT.value)
            for c in text
        ]

        self.vector_db.create_collection(collection_name,
                                        embedding_size=self.embedding_model.embedding_model_size,
                                        do_rest=do_rest)

        self.vector_db.insert_many(collection_name=collection_name, text=text,
                                    vector=vectors, metadata=metadata, record_id=chunk_ids)

        return True



    async def search_in_vector_db(self, project_id:str , query:str , limit: int=5):
        collection_name= await self.create_collection_name(project_id=project_id)

        vector= self.embedding_model.create_embeddings(text=query,document_type=CohertEnum.QUERY.value)

        results=self.vector_db.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)

        if not results:
            return False

        return results



    async def answer_using_RAG(self,project_id:str, query: str, limit: int=5 ):

        answer,full_prompt,chat_history=None,None,None

        #get the chunks the llm will use to answer
        chunks=self.search_in_vector_db(project_id=project_id,query=query,limit=limit)


        if not chunks or len(chunks)==0:
            return answer,full_prompt,chat_history

        system_prompt=self.tempalte_parser.get(group="rag",key="system_prompt")

        document_prompt="\n".join([
            self.tempalte_parser.get("rag","document_prompt",
                                     vars={
                                         "doc_num":idx+1,
                                         "chunk_text":doc
                                     })



                for idx,doc in enumerate(chunks)
            
        
        ]
        )

        footer_prompt=self.tempalte_parser.get("rag","footer_prompt")


        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ document_prompt,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history






    











        




