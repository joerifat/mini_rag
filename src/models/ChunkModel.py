from .BaseDataModel import BaseDataModel
from .schemas import Chunks
from .enums import DatabaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne


class ADD_Chunks(BaseDataModel):
    def __init__(self,clientdb):
        super().__init__(clientdb=clientdb)
        self.collection=clientdb[DatabaseEnum.COLLECTION_CHUNKS_NAME.value]

    async def add_chunk(self,chunk:Chunks):

        result= await self.collection.insert_one(chunk.dict())
        chunk._id=result.inserted_id

        return chunk
    
    async def get_chunk(self, chunk_id:str):

        result = await self.collection.find_one({"_id":ObjectId(chunk_id)})

        if result== None:
            chunk=Chunks(_id=chunk_id)
            new_chunk= await self.add_chunk(chunk=chunk)

            return new_chunk

        return Chunks(**result)
    
    async def add_many_chunks(self,chunks: list,batchsize: int =100 ):

        for i in range(0,len(chunks),batchsize):

            batch=chunks[i:i+batchsize]

            operations=[
                InsertOne(chunks.dict())
                for rec in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)
    
    async def delete_chunks_by_project_id(self,project_id: ObjectId):

        result= await self.collection.delete_many({"chunk_project_id":project_id})

        return result.delete_count








