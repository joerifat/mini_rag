from celeryapp import celery_app, setup_utils
import asyncio
from controllers import Process_controller
from models import UserResponses, Assets_Type
import logging
from models import Projects, ADD_Chunks, ASSETS
from models.schemas import Chunk
from utils.idempotancymanager import IdempotancyManager

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="tasks.processing.process_project_files",
    autoretry_for=(Exception,),
    retry_kwargs={
        "max_retries": 3,
        "countdown": 60
    },
)
def process_project_files(
    self,
    project_id: str,
    file_id: str,
    chunk_size: int,
    overlap_size: int,
    do_reset: int
):
    return asyncio.run(
        _process_project_files(
            self,
            project_id=project_id,
            Chunk_size=chunk_size,
            do_reset=do_reset,
            file_id=file_id,
            Chunk_overlap=overlap_size
        )
    )


async def _process_project_files(
    task_instance,
    project_id: str,
    file_id: str,
    Chunk_size: int,
    Chunk_overlap: int,
    do_reset: int
):

    db_engine = None
    vectordb_provider = None

    # هنحتاجهم في except لو حصل خطأ بعد إنشاء الـ record
    manager = None
    task_record = None

    try:
        (
            db_engine,
            client_db,
            llm_provider_factory,
            vectordb,
            generation_model,
            embedding_model,
            vectordb_provider,
            template_parser
        ) = await setup_utils()

        # ---------------------------------------------------------
        # 1) إنشاء Idempotency Manager
        # ---------------------------------------------------------
        manager = IdempotancyManager(
            db_client=client_db
        )

        # ---------------------------------------------------------
        # 2) تحديد البيانات التي تميز هذه الـ Task
        # ---------------------------------------------------------
        task_args = {
            "project_id": project_id,
            "file_id": file_id,
            "chunk_size": Chunk_size,
            "overlap_size": Chunk_overlap,
            "do_reset": do_reset
        }

        task_name = "tasks.processing.process_project_files"

        celery_task_id = task_instance.request.id

        # ---------------------------------------------------------
        # 3) هل المفروض ننفذ الـ Task أم لا؟
        # ---------------------------------------------------------
        should_execute, existing_task = await manager.should_execute_task(
            task_name=task_name,
            task_args=task_args,
            celery_task_id=celery_task_id,
            task_time_limit=600
        )

        # نفس التنفيذ موجود بالفعل ومش محتاج يتنفذ مرة أخرى
        if not should_execute:
            logger.warning(
                f"Task will not execute. Existing status: "
                f"{existing_task.status}"
            )

            return existing_task.result

        # ---------------------------------------------------------
        # 4) إنشاء record جديد أو استخدام الموجود
        # ---------------------------------------------------------
        if existing_task:
            task_record = existing_task

            await manager.update_task_status(
                execution_id=task_record.execution_id,
                status="PENDING"
            )

        else:
            task_record = await manager.create_task_record(
                task_name=task_name,
                task_args=task_args,
                celery_task_id=celery_task_id
            )

        # task بدأت التنفيذ الحقيقي
        await manager.update_task_status(
            execution_id=task_record.execution_id,
            status="STARTED"
        )

        # =========================================================
        # الكود الأصلي يبدأ من هنا
        # =========================================================

        add_to_clientdb = await Projects.call_two_functions(
            clientdb=client_db
        )

        project = await add_to_clientdb.get_project_or_create_one(
            project_id=project_id
        )

        asset = await ASSETS.call_two_functions(
            clientdb=client_db
        )

        asset_project_id = {}

        if file_id:
            result = await asset.get_one_file(
                asset_project_id=project.project_id,
                asset_name=file_id
            )

            if result is None:

                failure_result = {
                    "signal": UserResponses.FILE_ID_ERROR_VALUE.value,
                    "info": "No file with this name"
                }

                await manager.update_task_status(
                    execution_id=task_record.execution_id,
                    status="FAILURE",
                    result=failure_result
                )

                raise Exception(
                    f"No file with this name: {file_id}"
                )

            asset_project_id = {
                result.Asset_id: result.Asset_name
            }

        else:
            result = await asset.get_all_project_assets(
                asset_project_id=project.project_id,
                asset_type=Assets_Type.FILE.value
            )

            asset_project_id = {
                rec.Asset_id: rec.Asset_name
                for rec in result
            }

        if len(asset_project_id) == 0:

            failure_result = {
                "signal": UserResponses.NO_FILES_ERROR.value,
                "info": "No files for this project_id"
            }

            await manager.update_task_status(
                execution_id=task_record.execution_id,
                status="FAILURE",
                result=failure_result
            )

            raise Exception(
                f"No files for project_id: {project.project_id}"
            )

        ProcessController = Process_controller(
            project_id=project_id
        )

        chunks = await ADD_Chunks.call_two_functions(
            clientdb=client_db
        )

        if do_reset == 1:
            await chunks.delete_chunks_by_project_id(
                project_id=project.project_id
            )

        num_chunks = 0
        no_files = 0

        for asset_id, current_file_id in asset_project_id.items():

            file_content = ProcessController.get_file_content(
                file_id=current_file_id
            )

            if file_content is None:
                logger.info(
                    f"Error while processing file id {current_file_id}"
                )
                continue

            file_chunks = ProcessController.process_file_content(
                file_content=file_content,
                chunk_overlap=Chunk_overlap,
                chunk_size=Chunk_size,
                file_id=current_file_id
            )

            if file_chunks is None or len(file_chunks) == 0:

                failure_result = {
                    "signal": UserResponses.PROCESSING_FAILED.value,
                    "info": f"No chunks generated for {current_file_id}"
                }

                await manager.update_task_status(
                    execution_id=task_record.execution_id,
                    status="FAILURE",
                    result=failure_result
                )

                raise Exception(
                    f"Processing failed for file: {current_file_id}"
                )

            file_chunks_SchemeObject = [
                Chunk(
                    Chunk_text=i.page_content,
                    Chunk_metadata=i.metadata,
                    Chunk_project_id=project.project_id,
                    Chunk_asset_id=asset_id
                )
                for i in file_chunks
            ]

            num_chunks += await chunks.add_many_chunks(
                chunks=file_chunks_SchemeObject,
                batchsize=10
            )

            no_files += 1

        # ---------------------------------------------------------
        # 5) نجاح الـ Task
        # ---------------------------------------------------------

        success_result = {
            "signal": UserResponses.PROCESSING_SUCCESS.value,
            "len_chun": num_chunks,
            "processed_files": no_files,
            "project_id": project_id,
            "do_reset": do_reset
        }

        await manager.update_task_status(
            execution_id=task_record.execution_id,
            status="SUCCESS",
            result=success_result
        )

        return success_result

    except Exception as e:

        logger.error(
            f"Task failed: {str(e)}"
        )

        # لو الخطأ حصل بعد إنشاء task_record
        # ومكان الخطأ نفسه ما كانش حدث الحالة
        if manager and task_record:
            try:
                await manager.update_task_status(
                    execution_id=task_record.execution_id,
                    status="FAILURE",
                    result={
                        "error": str(e)
                    }
                )
            except Exception as status_error:
                logger.error(
                    f"Could not update idempotency task status: "
                    f"{str(status_error)}"
                )

        # مهم جدًا:
        # raise هي اللي تخلي Celery تشوف FAILURE/RETRY
        raise

    finally:
        try:
            if db_engine:
                await db_engine.dispose()

            if vectordb_provider:
                await vectordb_provider.disconnect()

        except Exception as e:
            logger.error(
                f"Task failed while cleaning: {str(e)}"
            )