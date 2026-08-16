from fastapi import APIRouter,Request,status
from fastapi.responses import JSONResponse
from models import Projects,ADD_Chunks
from models.enums import UserResponses
from controllers import NlpController
from .schemas.nlp import nlp_schema,SearchRequest
from tqdm import tqdm


nlp_router=APIRouter(
    prefix="/api/nlp",
    tags=["nlp"]
)

@nlp_router.post("/index/{project_id}")
async def index_into_vectordb(request:Request,project_id:int,schema:nlp_schema):#مفروض ان اي router اعرفلو schema

    project_model=await Projects.call_two_functions(clientdb=request.app.client_db)

    chunk_model=await ADD_Chunks.call_two_functions(clientdb=request.app.client_db)

    project=await project_model.get_project_or_create_one(project_id=project_id)



    nlp_controller=NlpController(vector_db=request.app.vectordb_provider,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model,
                                 template_parser=request.app.template_parser)


    collection_name=await nlp_controller.create_collection_name(project_id=project.project_id)

    _=await request.app.vectordb_provider.create_collection(collection_name=collection_name, embedding_size=request.app.embedding_model.embedding_model_size, do_rest=schema.do_rest)

    has_records=True
    number_of_vectors=0
    page=1
    

    while has_records:
        page_chunks= await chunk_model.get_chunks_by_project_id(project_id=project.project_id,page_no=page)

        if not page_chunks:
            has_records=False
            break

        page+=1

        chunk_ids=[
            c.Chunks_id
            for c in page_chunks
        ]



        is_inserted=await nlp_controller.index_into_vector_db(project_id=project_id,chunks=page_chunks,chunk_ids=chunk_ids,do_reset=schema.do_rest
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
async def get_collection_info(request:Request,project_id:int):
    nlp_controller=NlpController(vector_db=request.app.vectordb_provider,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model,
                                 template_parser=request.app.template_parser)

    collection_info=await nlp_controller.get_info_about_collection(project_id=project_id)

    return  JSONResponse(
        content={
            "signal": UserResponses.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model=await Projects.call_two_functions(clientdb=request.app.client_db)


    project=await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller=NlpController(vector_db=request.app.vectordb_provider,
                                 generation_model=request.app.generation_model,
                                 embedding_model=request.app.embedding_model,
                                 template_parser=request.app.template_parser)

    results = await nlp_controller.search_in_vector_db(
        project_id=project.project_id, query=search_request.text, limit=search_request.limit
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



@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model=await Projects.call_two_functions(clientdb=request.app.client_db)
    
    
    project=await project_model.get_project_or_create_one(project_id=project_id)
    
    nlp_controller=NlpController(vector_db=request.app.vectordb_provider,
                                        generation_model=request.app.generation_model,
                                        embedding_model=request.app.embedding_model,
                                        template_parser=request.app.template_parser)
    

    answer, full_prompt, chat_history =await nlp_controller.answer_using_RAG(
        project_id=project.project_id,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": UserResponses.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": UserResponses.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )
    