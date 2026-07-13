from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from .schemas import Project



class Projects(BaseDataModel):
    def __init__(self,clientdb : str):
        super().__init__(clientdb=clientdb)
        self.collection= clientdb[DatabaseEnum.COLLECTION_PROJECT_NAME.value]
    
    async def create_projects(self,project:Project):

        result= await self.collection.insert_one(project.dict())
        project._id= result.inserted_id
        return project
    

    async def get_project_or_create_one(self,project_id: str):
        
        record = await self.collection.find_one({"project_id":project_id})

        if record == None:
            project=Project(project_id=project_id)
            result= await self.create_projects(project=project)

            return project
        
        return Project(**record)
    
    async def get_all_projects(self , page: int = 1 , page_size : int =10):

        total_docs= await self.collection.count_documents({})

        total_pages= total_docs // page_size
        if total_docs % total_docs >0:
            total_pages += 1

        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)
        projects=[]
        for project in cursor:
            projects.append(Project(**project))

        return projects , total_pages

        


        


