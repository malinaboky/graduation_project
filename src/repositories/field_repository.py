import uuid

from sqlalchemy import insert, select

from src.database import async_session_maker
from src.schemas.field_schema import FieldSchemaGet
from src.domain.field import Field
from src.repositories.repository import SQLAlchemyRepository


class FieldRepository(SQLAlchemyRepository):
    model = Field

    async def add_all(self, data_list: list[dict]) -> dict[str, uuid.UUID]:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(data_list).returning(self.model)
            res = await session.scalars(stmt)
            await session.commit()
            return {x.name: x.id for x in res.all()}

    async def find_all(self, pipeline_id: uuid.UUID) -> list[Field]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.pipeline_id == pipeline_id)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res
