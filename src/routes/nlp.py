from fastapi import APIRouter,Request,status
from fastapi.responses import JSONResponse
from models import Projects,ADD_Chunks
from models.enums import UserResponses
from controllers import NlpController
from .schemas.nlp import nlp_schema,SearchRequest


nlp_router=APIRouter(
    prefix="/api/nlp",
    tags=["nlp"]
)

@nlp_router.post("/index/{project_id}")
async def index_into_vectordb(request:Request,project_id:str,schema:nlp_schema):#مفروض ان اي router اعرفلو schema

    project_model=await Projects.call_two_functions(clientdb=request.app.client_db)

    chunk_model=await ADD_Chunks.call_two_functions(clientdb=request.app.client_db)

    project=await project_model.get_project_or_create_one(project_id=project_id)



    nlp_controller=NlpController(vector_db=request.app.Vectordb,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model)

    has_records=True
    idx=0
    ids=[]
    number_of_vectors=0
    page=1
    

    while has_records:
        page_chunks= await chunk_model.get_chunks_by_project_id(project_id=project.id,page_no=page)

        if not page_chunks or len(page_chunks)==0:
            has_records=False
            break

        page+=1
        ids=list(range(idx,idx+len(page_chunks)))
        idx+=len(page_chunks)


        is_inserted=await nlp_controller.index_into_vector_db(project_id=project_id,chunks=page_chunks,chunk_ids=ids,
                                            )

        if not is_inserted:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "signal":UserResponses.PROBLEM_WHILE_INSERTING_TO_VECTORDB.value
                                })


        number_of_vectors+=len(page_chunks)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "signal":UserResponses.INDEXING_INTO_VECTORDB_SUCCESS.value,
                            "inserted_vecotrs":number_of_vectors
                        })


@nlp_router.get("/info/{project_id}")
async def get_collection_info(request:Request,project_id:str):
    nlp_controller=NlpController(vector_db=request.app.Vectordb,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model)

    collection_info=await nlp_controller.get_info_about_collection(project_id=project_id)

    return  JSONResponse(
        content={
            "signal": UserResponses.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model=await Projects.call_two_functions(clientdb=request.app.client_db)


    project=await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller=NlpController(vector_db=request.app.Vectordb,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model)

    results = nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": UserResponses.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": UserResponses.VECTORDB_SEARCH_SUCCESS.value,
            "results": [ result.dict()  for result in results ]
        }
    )



    