import uuid

from sqlalchemy import select

from src.database import async_session_maker
from src.domain.link import Link
from src.repositories.repository import SQLAlchemyRepository


class LinkRepository(SQLAlchemyRepository):
    model = Link

    async def find_one(self, pipeline_id: uuid.UUID) -> Link:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id)
            res = await session.execute(stmt)
            return [row[0] for row in res.all()][0]
