from .base_controller import BaseController
from models.schemas import Chunk
from stores.llm.llm_enums import CohertEnum
from typing import List
from stores.VectorDB.VectorDBEnum import PGVectorTableschema
import json


class NlpController(BaseController):
    def __init__(self,vector_db,generation_model,embedding_model,template_parser):
        self.vector_db=vector_db
        self.generation_model=generation_model
        self.embedding_model=embedding_model
        self.tempalte_parser=template_parser


    async def create_collection_name(self,project_id:str):
        return f"{PGVectorTableschema._PREFIX.value}_{self.vector_db.embedding_size}_{project_id}".strip()

    async def reset_vector_db_collection(self,project_id: str):
        collection_name= await self.create_collection_name(project_id=project_id)
        return await self.vector_db.delete_collection(collection_name=collection_name)




    async def get_info_about_collection(self,project_id:str):
        collection_name=await self.create_collection_name(project_id=project_id)
        collection_info=await self.vector_db.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )

    async def index_into_vector_db(self,project_id:str,chunks:List[Chunk],chunk_ids:List[int],do_reset:bool=False):

        collection_name=await self.create_collection_name(project_id=project_id)

        text=[
            c.Chunk_text
            for c in chunks
        ]

        metadata=[
            c.Chunk_metadata
            for c in chunks
        ]

        vectors=self.embedding_model.create_embeddings(text=text)

        await self.vector_db.insert_many(collection_name=collection_name, text=text,
                                    vector=vectors, metadata=metadata, record_id=chunk_ids)

        return True



    async def search_in_vector_db(self, project_id:str , query:str , limit: int=5):
        collection_name= await self.create_collection_name(project_id=project_id)

        vector= self.embedding_model.create_embeddings(text=query)

        results=await self.vector_db.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)

        if not results:
            return False

        return results



    async def answer_using_RAG(
    self,
    project_id: int,
    query: str,
    limit: int = 5
):

        answer, full_prompt, chat_history = None, None, None

        # 1. Retrieve relevant chunks
        chunks = await self.search_in_vector_db(
            project_id=project_id,
            query=query,
            limit=limit
        )

        if not chunks:
            return answer, full_prompt, chat_history

        # 2. System prompt
        system_prompt = self.tempalte_parser.get(
            group="rag",
            key="system_prompt"
        )

        # 3. Build retrieved documents context
        document_prompt = "\n".join([
            self.tempalte_parser.get(
                group="rag",
                key="document_prompt",
                vars={
                    "doc_num": idx + 1,
                    "chunk_text": doc.text
                }
            )
            for idx, doc in enumerate(chunks)
        ])

        # 4. Add user's question
        footer_prompt = self.tempalte_parser.get(
            group="rag",
            key="footer_prompt",
            vars={
                "query": query
            }
        )

        # 5. System message
        chat_history = [
            self.generation_model.construct_prompt(
                prompt=system_prompt,
                role=self.generation_model.enums.SYSTEM.value
            )
        ]

        # 6. User prompt
        full_prompt = "\n\n".join([
            document_prompt,
            footer_prompt
        ])

        # 7. Generate answer
        answer =  self.generation_model.generate_answer(user_prompt=full_prompt, chat_history =chat_history)

        return answer, full_prompt, chat_history

