import uuid

from sqlalchemy import select, desc

from src.database import async_session_maker
from src.domain.version import Version
from src.repositories.repository import SQLAlchemyRepository


class VersionRepository(SQLAlchemyRepository):
    model = Version

    async def find_one_by_pipeline(self, pipeline_id: uuid.UUID) -> Version:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id).order_by(desc(self.model.number))
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res[0] if len(res) > 0 else None

    async def find_all(self, pipeline_id: uuid.UUID) -> list[Version]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res
