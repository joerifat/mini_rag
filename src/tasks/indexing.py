from celeryapp import celery_app,setup_utils
import asyncio
from models import Projects,ADD_Chunks
from models.enums import UserResponses
from controllers import NlpController
import logging


logger=logging.getLogger(__name__)





@celery_app.task(bind=True,name="tasks.indexing.index_data",autoretry_for=(Exception,),
                 retry_kwargs={"max_retries":3,
                               "countdown":60})
def index_data(self,project_id:int,do_reset:bool):

    return asyncio.run(_index_data(self,project_id=project_id,do_reset=do_reset))



async def _index_data(task_instance,project_id:int,do_reset:bool):

    db_engine,vectordb_provider=None,None
    try:
        (db_engine, client_db, llm_provider_factory, vectordb,
            generation_model, embedding_model,vectordb_provider, template_parser)=await setup_utils()


        logger.info("The utils have been added sucessfuly")

        project_model=await Projects.call_two_functions(clientdb=client_db)

        chunk_model=await ADD_Chunks.call_two_functions(clientdb=client_db)

        project=await project_model.get_project_or_create_one(project_id=project_id)



        nlp_controller=NlpController(vector_db=vectordb_provider,
                                    generation_model=generation_model,
                                    embedding_model=embedding_model,
                                    template_parser=template_parser)


        collection_name=await nlp_controller.create_collection_name(project_id=project.project_id)

        _=await vectordb_provider.create_collection(collection_name=collection_name, embedding_size=embedding_model.embedding_model_size, do_rest=do_reset)

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



            is_inserted=await nlp_controller.index_into_vector_db(project_id=project_id,chunks=page_chunks,chunk_ids=chunk_ids,
                                                )

            if not is_inserted:
                task_instance.update_state(state="Failure",
                                    meta={
                                        "signal":UserResponses.PROBLEM_WHILE_INSERTING_TO_VECTORDB.value
                                    })
                return {
                    "signal":"not inserted"
                }


            number_of_vectors+=len(page_chunks)

        return {
                "signal":UserResponses.INDEXING_INTO_VECTORDB_SUCCESS.value,
                "inserted_vecotrs":number_of_vectors
            }


    except Exception as e:
        logger.error(f"Task faild {str(e)}")
        raise


    finally:
        if db_engine:
            await db_engine.dispose()
        if vectordb_provider:
            await vectordb_provider.disconnect()

    