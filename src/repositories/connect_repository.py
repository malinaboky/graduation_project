import uuid

from sqlalchemy import select

from src.database import async_session_maker
from src.domain.connection import Connection
from src.repositories.repository import SQLAlchemyRepository


class ConnectionRepository(SQLAlchemyRepository):
    model = Connection

    async def find_one(self, pipeline_id: uuid.UUID) -> Connection:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id)
            res = await session.execute(stmt)
            return res.scalar_one()
