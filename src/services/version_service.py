import uuid

from src.repositories.version_repository import VersionRepository
from src.domain.version import Version
from src.schemas.version_schema import VersionInfo
from src.schemas.version_schema import VersionSchemaAdd


class VersionService:
    def __init__(self, version_repo: VersionRepository):
        self.version_repo: VersionRepository = version_repo()

    async def create_version(self, pipeline_id: uuid.UUID) -> uuid.UUID:
        last_version: Version = await self.version_repo.find_one_by_pipeline(pipeline_id)
        version = VersionSchemaAdd(
            pipeline_id=pipeline_id,
            number=last_version.number+1 if last_version is not None else 0
        )
        version_id = await self.version_repo.add_one(version.model_dump())
        return version_id

    async def get_last_unready_version(self, pipeline_id: uuid.UUID) -> uuid.UUID:
        all_version = await self.version_repo.find_all(pipeline_id)
        if len(all_version) == 0:
            return None
        for v in all_version:
            if not v.is_done:
                return v.id
        return None

    async def get_all_version(self, pipeline_id: uuid.UUID) -> list[VersionInfo]:
        all_version: list[Version] = await self.version_repo.find_all(pipeline_id)
        if len(all_version) == 0:
            return None
        all_version.sort(key=lambda x: x.date)
        return [VersionInfo(id=v.id, is_done=v.is_done, name=f'Версия ({str(v.date.date())})') for v in all_version]

    async def get_done_version(self, pipeline_id: uuid.UUID) -> list[VersionInfo]:
        all_version: list[Version] = await self.version_repo.find_all(pipeline_id)
        if len(all_version) == 0:
            return None
        return [VersionInfo(id=v.id, is_done=v.is_done, name=f'Версия ({str(v.date.date())})') for v in all_version if v.is_done]

    async def get_version(self, version_id: uuid.UUID) -> VersionInfo:
        version: Version = await self.version_repo.find_one(version_id)
        return VersionInfo(id=version.id, is_done=version.is_done, name=f'Версия ({str(version.date.date())})')

    async def delete(self, id: uuid.UUID):
        return await self.version_repo.delete(id)

    async def set_done(self, id: uuid.UUID):
        return await self.version_repo.update(id, {"is_done": True})
