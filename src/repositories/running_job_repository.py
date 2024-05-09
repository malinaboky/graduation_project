import uuid

from sqlalchemy import update

from src.database import async_session_maker
from src.domain.running_job import RunningJob
from src.repositories.repository import SQLAlchemyRepository


class RunningJobRepository(SQLAlchemyRepository):
    model = RunningJob

    async def update(self, id: uuid.UUID, job_id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == id).values(job_id=job_id)
            await session.execute(stmt)
            await session.commit()
            return
