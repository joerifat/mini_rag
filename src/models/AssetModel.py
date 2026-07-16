from .schemas import Assets
from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from bson.objectid import ObjectId
import logging

class ASSETS(BaseDataModel):

    def __init__(self,clientdb: str):
        super().__init__(clientdb=clientdb)
        self.collection=self.clientdb[DatabaseEnum.COLLECTION_ASSETS_NAME.value]

    
    @classmethod
    async def call_two_functions(cls,clientdb: str):
        instance= cls(clientdb)
        await instance.init_collection()
        return instance


    

    async def init_collection(self):

        all_collections= await self.clientdb.list_collection_names()

        if DatabaseEnum.COLLECTION_ASSETS_NAME.value not in all_collections:
            self.collection=self.clientdb[DatabaseEnum.COLLECTION_ASSETS_NAME.value]
            indexs=Assets.index_settings()
            for index in indexs:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_asset(self, asset:Assets):

        result= await self.collection.insert_one(asset.dict(by_alias=True,exclude_unset=True))
        asset.id=result.inserted_id

        return asset


    async def get_all_project_assets(self ,asset_project_id : str , asset_type: str):

        result= await self.collection.find({
            "asset_project_id":ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_type":asset_type
        }).to_list(length=None)

        return [
            Assets(**result)
            for rec in result
            ]
    

    async def get_one_file(self,asset_project_id : str, asset_name: str ):

        result=self.collection.find_one({
            "asset_project_id":ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_name":asset_name
        })

        if result:
            return Assets(**result)
        
        return None