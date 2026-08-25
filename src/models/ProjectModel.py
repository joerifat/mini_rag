from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from .schemas import Project
from sqlalchemy import select,func



class Projects(BaseDataModel):
    def __init__(self,clientdb : str):
        super().__init__(clientdb=clientdb)
        self.clientdb=clientdb

    @classmethod
    async def call_two_functions(cls,clientdb : str):
        instance=cls(clientdb)
        return instance

    
    async def create_projects(self,project:Project):
        async with self.clientdb() as session:
            async with session.begin():
                session.add(project)
            await session.refresh(project)

        return project

    

    async def get_project_or_create_one(self,project_id: str):
        async with self.clientdb() as session:
            async with session.begin():
                query=select(Project).where(Project.project_id==project_id)
                result=await session.execute(query)
                project=result.scalar_one_or_none()


                if project is None:
                    project = Project(project_id=project_id)
                    session.add(project)

            await session.refresh(project)
            return project

                
        
    
    async def get_all_projects(self , page: int = 1 , page_size : int =10):

        async with self.clientdb() as session:
            async with session.begin():

                total_docs= await session.execute(select(func.count(Project.project_id)))
                total_docs= total_docs.scalar_one()

                total_pages=total_docs//page_size
                if total_docs%page_size>0:
                    total_pages+=1

                query=select(Project).offset((page-1)*page_size).limit(page_size)
                result=await session.execute(query)
                projects= result.scalars().all()

                return projects,total_pages

       