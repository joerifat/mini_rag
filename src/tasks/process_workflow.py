from celery import chain
from celeryapp import celery_app,setup_utils
from .processing import process_project_files
from .indexing import _index_data
import asyncio

@celery_app.task(bind=True,name="tasks.process_workflow.push_after_processing",autoretry_for=(Exception,),
                 retry_kwargs={
                    "max_retries":3,
                     "countdown":60
                 })


def push_after_processing(self,prev_task_result):

    project_id=prev_task_result.get("project_id")
    do_reset=prev_task_result.get("do_reset")

    task_result= asyncio.run(_index_data(self,project_id=project_id,do_reset=do_reset))

    return {
        "project_id": project_id,
        "do_reset": do_reset,
        "task_results": task_result
    }








@celery_app.task(bind=True,name="tasks.process_workflow.process_and_push",autoretry_for=(Exception,),
                 retry_kwargs={
                    "max_retries":3,
                     "countdown":60
                 })


def process_and_push(self,project_id:str,file_id:str,chunk_size:int,overlap_size:int,do_reset:int):


    workflow=chain(
        process_project_files.s(project_id,file_id,chunk_size,overlap_size,do_reset),
        push_after_processing.s()
    )

    result= workflow.apply_async()

    return {
        "signal":"Workflow is started",
        "workflow_id":result.id,
        "tasks":["process_project_files","index_data"]
    }