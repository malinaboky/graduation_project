import asyncio
from datetime import datetime

from src.config import MAX_TASK_COUNT
from src.services.pipeline_service import DataPipelineService


class JobManager:
    def __init__(self, data_pipeline_service, running_job_service):
        self.pipeline_service: DataPipelineService = data_pipeline_service()
        self.running_job_service = running_job_service

    async def check_pipelines(self, background_tasks: set):
        current_time = datetime.utcnow()
        pipelines = await self.pipeline_service.get_all_idle_pipeline(current_time)
        for pipeline in pipelines:
            if len(background_tasks) < MAX_TASK_COUNT:
                task = asyncio.create_task(self.running_job_service().run_pipeline(pipeline))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
