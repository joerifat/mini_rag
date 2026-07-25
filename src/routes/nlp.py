from fastapi import APIRouter,Request,status,Depends
from fastapi.responses import JSONResponse
from models import Projects,ADD_Chunks
from controllers import NlpController
from models import UserResponses
from .schemas.nlp import PushRequest
import logging

logger=logging.getLogger("uvicorn.error")

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id: str,pushrequest:PushRequest):

    project_model=Projects(clientdb=request.app.client_db)
    chunk_model=ADD_Chunks(clientdb=request.app.client_db)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal":"No such project id in projects collection"
                            })

    nlp_controller=NlpController(vectordb_client=request.app.Vectordb,
                                 embedding_model=request.app.embedding_model,
                                 generation_model=request.app.generation_model)

    has_records=1
    page_no=1
    idx=0
    inserted_vectors=0

    while has_records:
        page_chunks= await chunk_model.get_chunks_by_project_id(project_id=project.id,page_no=page_no)

        if not page_chunks:
            has_records=False
            break

        page_no+=1
        chunk_ids=list(range(idx,len(page_chunks)))
        idx+=len(page_chunks)

        
        is_inserted=nlp_controller.index_into_vectordb(project=project,chunks=page_chunks,
                                                        chunks_ids=chunk_ids,
                                                        do_rest=pushrequest.do_rest)

        if not is_inserted:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "signal":UserResponses.PROBLEM_WHILE_INSERTING_TO_VECTORDB.value
                                })

        inserted_vectors+=len(page_chunks)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={
                                "signal":UserResponses.INDEXING_INTO_VECTORDB_SUCCESS.value,
                                "inserted_vectors":inserted_vectors
                            })

@nlp_router.get("/index/info/{project_id}")
async def get_info_about_collection(request: Request,project_id: str):

    project_model=Projects(clientdb=request.app.client_db)

    project=project_model.get_project_or_create_one(project_id=project_id)

    
    nlp_controller=NlpController(vectordb_client=request.app.Vectordb,
                                 embedding_model=request.app.embedding_model,
                                 generation_model=request.app.generation_model)

    collection_info=nlp_controller.get_vector_db_collection_info(project_id=project_id)

    return JSONResponse(
        content={
            "signal": UserResponses.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.
    
    











    

     

    










    

















    











