from .BaseDataModel import BaseDataModel
from .schemas import Chunks
from .enums import DatabaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import List


class ADD_Chunks(BaseDataModel):
    def __init__(self,clientdb):
        super().__init__(clientdb=clientdb)
        self.collection=clientdb[DatabaseEnum.COLLECTION_CHUNKS_NAME.value]

    @classmethod
    async def call_two_functions(cls,clientdb : str):
        instance=cls(clientdb)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections= await self.clientdb.list_collection_names()

        if DatabaseEnum.COLLECTION_CHUNKS_NAME.value not in all_collections:
            self.collection = self.clientdb[DatabaseEnum.COLLECTION_CHUNKS_NAME.value]
            indexs=Chunks.index_settings()
            for index in indexs:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )


    

    async def add_chunk(self,chunk:Chunks):

        result= await self.collection.insert_one(chunk.dict(by_alias=True,exclude_unset=True))
        chunk.id=result.inserted_id

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
                InsertOne(rec.dict(by_alias=True,exclude_unset=True))
                for rec in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)
    
    async def delete_chunks_by_project_id(self,project_id: ObjectId):

        result= await self.collection.delete_many({"chunk_project_id":project_id})

        return result.deleted_count



    async def get_chunks_by_project_id(self,project_id: ObjectId,page_no: int , page_size: int=50) ->List:

        if not project_id:
            return False

        records= await self.collection.find({
            "chunk_project_id":project_id,
        }).skip((page_no-1)*page_size).limit(page_size).to_list(length=None)

        return [
            Chunks(**record)
            for record in records
        ]












