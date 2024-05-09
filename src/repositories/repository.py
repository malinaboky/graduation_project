import uuid
from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete

from src.database import async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> uuid.UUID:
        raise NotImplementedError

    @abstractmethod
    async def add_all(self, data_list: list[dict]):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: uuid.UUID):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: uuid.UUID):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: uuid.UUID, data: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> uuid.UUID:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def add_all(self, data_list: list[dict]) -> list[uuid.UUID]:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(data_list).returning(self.model.id)
            res = await session.scalars(stmt)
            await session.commit()
            return res.all()

    async def find_one(self, id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            return res.scalar_one()

    async def find_all(self):
        async with async_session_maker() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res

    async def update(self, id: uuid.UUID, data: dict):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == id).values(data)
            await session.execute(stmt)
            await session.commit()
            return

    async def delete(self, id: uuid.UUID):
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == id)
            await session.execute(stmt)
            await session.commit()
            return
