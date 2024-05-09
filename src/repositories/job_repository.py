import uuid

from sqlalchemy import select

from src.database import async_session_maker
from src.domain.job import Job
from src.repositories.repository import SQLAlchemyRepository


class JobRepository(SQLAlchemyRepository):
    model = Job

    async def find_all(self, pipeline_id: uuid.UUID) -> list[Job]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id)
            res = await session.execute(stmt)
            return [row[0] for row in res.all()]
