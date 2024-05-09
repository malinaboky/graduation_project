import uuid

from sqlalchemy import select, func, and_, delete, update, case, insert, text, distinct

from src.database import async_session_maker
from src.domain.data import Data
from src.domain.data_tmp import DataTMP
from src.config import MAX_ROW_COUNT
from src.repositories.repository import SQLAlchemyRepository


class DataRepository(SQLAlchemyRepository):
    model = Data
    model_tmp = DataTMP

    async def update_batch_data(self, version_id: uuid.UUID, new_val: list[dict]):
        async with async_session_maker() as session:
            stmt = insert(self.model_tmp).values(new_val).returning(self.model_tmp.id)
            await session.scalars(stmt)
            stmt = f"UPDATE data d SET value = dtmp.value " \
                   f"FROM data_tmp dtmp WHERE d.id = dtmp.data_id"
            await session.execute(text(stmt))
            stmt = delete(self.model_tmp).where(self.model_tmp.version_id == version_id)
            await session.execute(stmt)
            await session.commit()
            return

    async def get_batch_for_x_y(self, x_direct: uuid.UUID, y_direct: uuid.UUID, version_id: uuid.UUID,
                                start: int, end: int) -> list[tuple]:
        async with async_session_maker() as session:
            query = f"SELECT d_x.value as x_value, d_y.value as y_value " \
                    f"FROM data d_x left join data d_y on d_x.row_id = d_y.row_id and d_x.version_id = d_y.version_id " \
                    f"WHERE d_x.version_id = '{version_id}' and d_x.field_id = '{x_direct}' and d_y.field_id = '{y_direct}' " \
                    f"LIMIT {end - start} OFFSET {start};"
            stmt = text(query)
            res = await session.execute(stmt)
            return res.all()

    async def count_data_by_version(self, version_id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = select(func.count()).where(self.model.version_id == version_id).select_from(self.model)
            res = await session.execute(stmt)
            return res.scalar()

    async def count_for_x_y(self, x_direct: uuid.UUID, y_direct: uuid.UUID, version_id: uuid.UUID) -> int:
        async with async_session_maker() as session:
            query = f"SELECT COUNT(*) " \
                    f"FROM data d_x left join data d_y on d_x.row_id = d_y.row_id and d_x.version_id = d_y.version_id " \
                    f"WHERE d_x.version_id = '{version_id}' and d_x.field_id = '{x_direct}' and d_y.field_id = '{y_direct}';"
            stmt = text(query)
            res = await session.execute(stmt)
            return res.scalar_one()

    async def get_batch_for_x_all(self, x_direct: uuid.UUID, version_id: uuid.UUID, start: int, end: int) -> list[tuple]:
        async with async_session_maker() as session:
            stmt = select(self.model.value)\
                .where(and_(self.model.field_id == x_direct, self.model.version_id == version_id)).slice(start, end)
            res = await session.execute(stmt)
            return res.all()

    async def count_for_x_all(self, x_direct: uuid.UUID, version_id: uuid.UUID) -> int:
        async with async_session_maker() as session:
            stmt = select(func.count()).where(and_(self.model.field_id == x_direct, self.model.version_id == version_id))
            res = await session.execute(stmt)
            return res.scalar_one()

    async def get_batch_for_x_unique(self, x_direct: uuid.UUID, version_id: uuid.UUID, start: int, end: int) -> list[tuple]:
        async with async_session_maker() as session:
            stmt = select(distinct(self.model.value)) \
                .where(and_(self.model.field_id == x_direct, self.model.version_id == version_id)).slice(start, end)
            res = await session.execute(stmt)
            return res.all()

    async def count_for_x_unique(self, x_direct: uuid.UUID, version_id: uuid.UUID) -> int:
        async with async_session_maker() as session:
            stmt = select(func.count(distinct(self.model.value)))\
                .where(and_(self.model.field_id == x_direct, self.model.version_id == version_id))
            res = await session.execute(stmt)
            return res.scalar_one()

    async def get_batch_data(self, version_id: uuid.UUID, field_id: uuid.UUID, skip_row) -> list[Data]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .slice(skip_row, skip_row+MAX_ROW_COUNT)
            res = await session.execute(stmt)
            return [row[0] for row in res.all()]

    async def get_batch_data_with_src_struct(self, version_id: uuid.UUID, skip_row: int, limit: int) -> list[Data]:
        async with async_session_maker() as session:
            query = f"SELECT r.id, r.number, f.name, d.value " \
                    f"FROM row r LEFT JOIN data d on r.id = d.row_id LEFT JOIN field f ON d.field_id = f.id " \
                    f"WHERE r.version_id = '{version_id}' ORDER BY number, column_number "\
                    f"LIMIT {limit} OFFSET {skip_row};"
            stmt = text(query)
            res = await session.execute(stmt)
            return res.all()

    async def get_batch_empty_data(self, version_id: uuid.UUID, field_id: uuid.UUID, skip_row) -> list[Data]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .where(self.model.value == "").slice(skip_row, skip_row+MAX_ROW_COUNT)
            res = await session.execute(stmt)
            return [row[0] for row in res.all()]

    async def get_batch_full_data(self, version_id: uuid.UUID, field_id: uuid.UUID, skip_row: int) -> list[Data]:
        async with async_session_maker() as session:
            stmt = select(self.model).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .where(self.model.value != "").slice(skip_row, skip_row+MAX_ROW_COUNT)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res

    async def count_data_by_field(self, version_id: uuid.UUID, field_id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = select(func.count()).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .select_from(self.model)
            res = await session.execute(stmt)
            return res.scalar()

    async def count_empty_data_by_field(self, version_id: uuid.UUID, field_id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = select(func.count()).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .where(self.model.value == "").select_from(self.model)
            res = await session.execute(stmt)
            return res.scalar()

    async def count_full_data_by_field(self, version_id: uuid.UUID, field_id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = select(func.count()).where(and_(self.model.version_id == version_id, self.model.field_id == field_id))\
                .where(self.model.value != "").select_from(self.model)
            res = await session.execute(stmt)
            return res.scalar()
