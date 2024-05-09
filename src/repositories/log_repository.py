import uuid

from sqlalchemy import select, desc

from src.database import async_session_maker
from src.domain.log import Log
from src.repositories.repository import SQLAlchemyRepository


class LogRepository(SQLAlchemyRepository):
    model = Log

    async def find_one(self, pipeline_id: uuid.UUID) -> Log:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id).order_by(desc(self.model.date))
            res = await session.execute(stmt)
            return res.first()
