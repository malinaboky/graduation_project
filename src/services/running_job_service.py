import uuid

from src.schemas.running_job_schema import RunningJobSchemaAdd
from src.repositories.running_job_repository import RunningJobRepository


class RunningJobService:
    def __init__(self, running_job_repo: RunningJobRepository):
        self.running_job_repo: RunningJobRepository = running_job_repo()

    async def create_running_job(self, pipeline_id: uuid.UUID, job_id: uuid.UUID) -> uuid.UUID:
        job = RunningJobSchemaAdd(
            pipeline_id=pipeline_id,
            job_id=job_id
        )
        return await self.running_job_repo.add_one(job.model_dump())

    async def delete(self, id: uuid.UUID):
        return await self.running_job_repo.delete(id)

    async def update(self, id: uuid.UUID, job_id: uuid.UUID):
        return await self.running_job_repo.update(id, job_id)
