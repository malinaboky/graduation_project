import uuid
from datetime import datetime

from src.domain.data_pipeline import DataPipeline
from src.services import time_lag_service
from src.repositories.pipeline_repository import DataPipelineRepository
from src.schemas.pipeline_schema import PipelineSchemaAdd, PipelineSchemaGet, PipelineSchemaTypeResGet, PipelineSchemaUpdate
from src.schemas.enums.resource_type import ResourceType


class DataPipelineService:
    def __init__(self, pipeline_repo: DataPipelineRepository):
        self.pipeline_repo: DataPipelineRepository = pipeline_repo()

    async def create_pipeline(self, name: str, type: str, user_id: uuid.UUID,
                              period: str = None, period_val: int = None) -> uuid.UUID:
        new_pipeline = PipelineSchemaAdd(
            user_id=user_id,
            name=name,
            type_res=ResourceType[type].name,
            min_time_lag=time_lag_service.generate_time_lag(period, period_val) if period is not None else 0
        )
        return await self.pipeline_repo.add_one(new_pipeline.model_dump())

    async def find_pipeline(self, id: uuid.UUID) -> DataPipeline:
        return await self.pipeline_repo.find_one(id)

    async def get_user_pipelines(self, user_id: uuid.UUID) -> list[PipelineSchemaGet]:
        pipelines: list[DataPipeline] = await self.pipeline_repo.find_all(user_id)
        return [PipelineSchemaGet(id=x.id, name=x.name, pause=x.pause) for x in pipelines]

    async def update_pipeline_after_run(self, pipeline_info: PipelineSchemaTypeResGet):
        current_time = datetime.utcnow().replace(second=0, microsecond=0)
        update_info = PipelineSchemaUpdate(
            pause=ResourceType[pipeline_info.type_res] == ResourceType.file,
            date=current_time
        )
        return await self.pipeline_repo.update(pipeline_info.id, update_info.model_dump())

    async def set_on_pause(self, id):
        return await self.pipeline_repo.update(id, {"pause": True})

    async def delete(self, id):
        return await self.pipeline_repo.delete(id)

    async def get_all_idle_pipeline(self, current_time: datetime):
        pipelines = await self.pipeline_repo.find_all_pipelines_not_on_pause(current_time)
        return [PipelineSchemaTypeResGet(id=x[0], user_id=x[1], type_res=x[2]) for x in pipelines]

