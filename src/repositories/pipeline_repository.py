import uuid
from datetime import datetime

from sqlalchemy import select, insert, func, text

from src.database import async_session_maker
from src.domain.data_pipeline import DataPipeline
from src.repositories.repository import SQLAlchemyRepository


class DataPipelineRepository(SQLAlchemyRepository):
    model = DataPipeline

    async def find_all(self, user_id: uuid.UUID) -> list[DataPipeline]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.user_id == user_id)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res

    async def add_one(self, data: dict) -> uuid.UUID:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_all_pipelines_not_on_pause(self, current_time: datetime):
        query = f"select data_pipeline.id, data_pipeline.user_id, data_pipeline.type_res from data_pipeline " \
                f"left join running_job rj on data_pipeline.id = rj.pipeline_id " \
                f"where pause is FALSE  and " \
                f"(date is NULL or (date + (min_time_lag * interval '1 minute') <= TO_TIMESTAMP('{current_time}', 'YYYY-MM-DD HH24:MI:ss'))) " \
                f"and rj.pipeline_id is NULL;"
        async with async_session_maker() as session:
            stmt = text(query)
            res = await session.execute(stmt)
            return res.all()
