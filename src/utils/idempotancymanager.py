import hashlib
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from models.schemas.minirag.postgresSchema import Celery_tasks



class IdempotancyManager:

    def __init__(self,db_client):
        self.db_client=db_client




    def create_args_hash(self,task_name:str,task_args:dict):

        combined_data={
            **task_args,
            "task_name":task_name
        }

        json_string=json.dumps(combined_data,sort_keys=True,default=str)

        return hashlib.sha256(json_string.encode()).hexdigest()



    async def create_task_record(self,task_name:str,task_args:dict,celery_task_id=None):

        task_hash= self.create_args_hash(task_name=task_name,task_args=task_args)

        task_records=Celery_tasks(task_name=task_name,task_args_hash=task_hash,
                                  celery_task_id=celery_task_id,
                                  status="STARTED",started_at=datetime.utcnow(),
                                  task_args=task_args
                                  )

        try:
            async with self.db_client() as session:
                async with session.begin():
                    session.add(task_records)
                await session.refresh(task_records)
            return  task_records

        finally:
            await session.close()



    async def update_task_status(self, execution_id: int, status: str, result: dict = None):
        """Update task status and result."""
        session = self.db_client()
        try:
            task_record = await session.get(Celery_tasks, execution_id)
            if task_record:
                task_record.status = status
                if result:
                    task_record.result = result
                if status in ['SUCCESS', 'FAILURE']:
                    task_record.completed_at = datetime.utcnow()
                await session.commit()
        finally:
            await session.close()

    async def get_existing_task(self, task_name: str, 
                                task_args: dict, celery_task_id: str) -> Celery_tasks:
        """Check if task with same name and args already exists."""
        args_hash = self.create_args_hash(task_name, task_args)
        
        session = self.db_client()
        try:
            stmt = select(Celery_tasks).where(
                Celery_tasks.celery_task_id == celery_task_id,
                Celery_tasks.task_name == task_name,
                Celery_tasks.task_args_hash == args_hash
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        finally:
            await session.close()

    async def should_execute_task(self, task_name: str, task_args: dict,
                                  celery_task_id: str, 
                                  task_time_limit: int = 600) -> tuple[bool, Celery_tasks]:
        """
        Check if task should be executed or return existing result.
        Args:
            task_time_limit: Time limit in seconds after which a stuck task can be re-executed
        Returns (should_execute, existing_task_or_none)
        """
        existing_task = await self.get_existing_task(task_name, task_args, celery_task_id)
        
        if not existing_task:
            return True, None
            
        # Don't execute if task is already completed successfully
        if existing_task.status == 'SUCCESS':
            return False, existing_task
            
        # Check if task is stuck (running longer than time limit + 60 seconds)
        if existing_task.status in ['PENDING', 'STARTED', 'RETRY']:
            if existing_task.started_at:
                time_elapsed = (datetime.utcnow() - existing_task.started_at).total_seconds()
                time_gap = 60  # 60 seconds grace period
                if time_elapsed > (task_time_limit + time_gap):
                    return True, existing_task  # Task is stuck, allow re-execution
            return False, existing_task  # Task is still running within time limit
            
        # Re-execute if previous task failed
        return True, existing_task


    async def cleanup_old_tasks(self, time_retention: int = 86400) -> int:

        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_retention)
        
        session = self.db_client()
        try:
            stmt = delete(Celery_tasks).where(
                Celery_tasks.created_at < cutoff_time
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        finally:
            await session.close()
    

        





    