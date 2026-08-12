from .schemas import Asset
from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from bson.objectid import ObjectId
from sqlalchemy import select

class ASSETS(BaseDataModel):

    def __init__(self,clientdb : str):
        super().__init__(clientdb=clientdb)
        self.clientdb=clientdb

    @classmethod
    async def call_two_functions(cls,clientdb : str):
        instance=cls(clientdb)
        return instance

    async def create_asset(self, asset:Asset):
        async with self.clientdb() as session:
            async with session.begin():
                session.add(asset)
            await session.refresh(asset)

        return asset



    async def get_all_project_assets(self ,asset_project_id : str , asset_type: str):
        async with self.clientdb() as session:
            async with session.begin():
              query = (
                    select(Asset)
                    .where(Asset.Asset_project_id == asset_project_id,
                           Asset.Asset_type==asset_type)
              )

              result = await session.execute(query)
              records= result.scalars().all()

        return records
    

    async def get_one_file(self,asset_project_id : str, asset_name: str ):
        async with self.clientdb() as session:
            async with session.begin():
              query = (
                    select(Asset)
                    .where(Asset.Asset_project_id == asset_project_id,
                           Asset.Asset_name==asset_name)
              )

              result = await session.execute(query)
              record = result.scalar_one_or_none()

        return record


