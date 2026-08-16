from .BaseDataModel import BaseDataModel
from .schemas import Chunk
from .enums import DatabaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import List
from sqlalchemy import select,func,delete


class ADD_Chunks(BaseDataModel):
    def __init__(self,clientdb : str):
        super().__init__(clientdb=clientdb)
        self.clientdb=clientdb

    @classmethod
    async def call_two_functions(cls,clientdb : str):
        instance=cls(clientdb)
        return instance
    

    async def add_chunk(self,chunk:Chunk):
        async with self.clientdb() as session:
            async with session.begin():
                session.add(chunk)
            await session.refresh(chunk)

        return chunk
    
    async def get_chunk(self, chunk_id:str):
        async with self.clientdb() as session:
            async with session.begin():
                query=select(Chunk).where(Chunk.Chunks_id==chunk_id)
                result= await session.execute(query)
                chunk= result.scalar_one_or_none()
            return chunk
    
    async def add_many_chunks(self,chunks: list,batchsize: int =100 ):
        async with self.clientdb() as session:
            async with session.begin():
                for i in range(0,len(chunks),batchsize):
                    batch=chunks[i:i+batchsize]
                    session.add_all(batch)


        return len(chunks)
                


    
    async def delete_chunks_by_project_id(self,project_id: ObjectId):
        async with self.clientdb() as session:
            async with session.begin():
                query=delete(Chunk).where(Chunk.Chunk_project_id==project_id)
                result= await session.execute(query)

        return result.rowcount




    async def get_chunks_by_project_id(self,project_id: ObjectId,page_no: int , page_size: int=50) ->List:
        async with self.clientdb() as session:
            async with session.begin():
              query = (
                    select(Chunk)
                    .where(Chunk.Chunk_project_id == project_id)
                    .offset((page_no - 1) * page_size)
                    .limit(page_size)
                )

              result = await session.execute(query)
              records= result.scalars().all()

        return records














