import uuid

from src.domain.log import Log
from src.schemas.log_schema import LogSchemaAdd
from src.schemas.enums.status_code import StatusCode
from src.repositories.log_repository import LogRepository


class LogService:
    def __init__(self, log_repo: LogRepository):
        self.log_repo: LogRepository = log_repo()

    async def log_ok(self, pipeline_id: uuid.UUID) -> uuid.UUID:
        log = LogSchemaAdd(
            pipeline_id=pipeline_id,
            status=StatusCode.ok
        )
        return await self.log_repo.add_one(log.model_dump())

    async def log_error(self, pipeline_id: uuid.UUID, message: str) -> uuid.UUID:
        log = LogSchemaAdd(
            pipeline_id=pipeline_id,
            status=StatusCode.error,
            message=message
        )
        return await self.log_repo.add_one(log.model_dump())

    async def get_last_log(self, pipeline_id: list[uuid.UUID]) -> list[Log]:
        logs = []
        for p_id in pipeline_id:
            cur_log = await self.log_repo.find_one(p_id)
            logs.append(cur_log)
        return logs
