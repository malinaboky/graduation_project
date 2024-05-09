import json
import uuid
from typing import Any

from pydantic import ValidationError

from src.repositories.job_repository import JobRepository
from src.domain.job import Job
from src.schemas.job_schema import JobSchemaAdd
from src.schemas.field_schema import FieldInfo, FieldSchemaGet
from src.schemas.enums.job_type import Param
from src.schemas.enums.job_type import JobType


class JobService:
    def __init__(self, job_repo: JobRepository):
        self.job_repo: JobRepository = job_repo()

    async def create_jobs_for_db(self, pipeline_id: uuid.UUID,
                                   form_fields: list[FieldInfo],
                                   added_fields: dict[str, uuid.UUID],
                                   date_field: str) -> list[uuid.UUID]:

        job_list = []
        order = 0
        job_list.append(JobSchemaAdd(
            pipeline_id=pipeline_id,
            order=order,
            type=JobType.load_db.name,
            params={} if date_field is None or date_field == "" else {"date_field": date_field}
        ).model_dump())
        for field in form_fields:
            for job in field.job_list:
                order = order + 1
                job_list.append(JobSchemaAdd(
                    pipeline_id=pipeline_id,
                    field_id=added_fields[field.field_name],
                    order=order,
                    type=JobType[job.name].name,
                    params={job.param[i]: job.param_value[i] for i in range(len(job.param))} if len(job.param) > 0 else {}
                ).model_dump())
        return await self.job_repo.add_all(job_list)

    async def create_jobs_for_file(self, pipeline_id: uuid.UUID,
                                   sep: str,
                                   auto_title: bool,
                                   form_fields: list[FieldInfo],
                                   added_fields: dict[str, uuid.UUID],
                                   preload: bool = True) -> list[uuid.UUID]:
        job_list = []
        order = 0
        if preload:
            job_list.append(JobSchemaAdd(
                pipeline_id=pipeline_id,
                order=order,
                type=JobType.download.name,
                params={}
            ).model_dump())
            order = order + 1
        job_list.append(JobSchemaAdd(
            pipeline_id=pipeline_id,
            order=order,
            type=JobType.load_file.name,
            params={Param.sep.name: sep, Param.auto_title.name: auto_title} if sep else {Param.auto_title.name: auto_title}
        ).model_dump())
        for field in form_fields:
            for job in field.job_list:
                order = order + 1
                job_list.append(JobSchemaAdd(
                    pipeline_id=pipeline_id,
                    field_id=added_fields[field.field_name],
                    order=order,
                    type=JobType[job.name].name,
                    params={job.param[i]: job.param_value[i] for i in range(len(job.param))} if len(job.param) > 0 else {}
                ).model_dump())
        return await self.job_repo.add_all(job_list)

    async def get_all_jobs_of_pipeline(self, pipeline_id: uuid.UUID) -> list[Job]:
        jobs: list[Job] = await self.job_repo.find_all(pipeline_id)
        jobs.sort(key=lambda x: x.order)
        return jobs

    async def update_job(self, id: uuid.UUID, values: dict[str, Any]):
        return await self.job_repo.update(id, values)
