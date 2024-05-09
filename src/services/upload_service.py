import csv
import json
import time
from datetime import datetime
import uuid

import pandas as pd
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from sqlalchemy import MetaData, select, func, text, or_
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.testing.schema import Table

from src.schemas.enums.field_type import FieldType
from src.domain.connection import Connection
from src.schemas.enums.connection_type import ConnectionType
from src.exceptions.upload_file_exception import UploadFileError
from src.exceptions.upload_db_exception import UploadDbError
from src.schemas.enums.file_type import FileType
from src.services.data_service import DataService
from src.services.row_service import RowService
from src.services import foreign_connect_service
from src.services import cast_type_service
from src.services.version_service import VersionService
from src.domain.field import Field
from src.config import MAX_ROW_COUNT


class UploadService:
    def __init__(self, version_service: VersionService,
                 row_service: RowService,
                 data_service: DataService):
        self._version_service: VersionService = version_service()
        self._row_service: RowService = row_service()
        self._data_service: DataService = data_service()

    def _read_csv(self, file_path: str, auto_title: bool, sep: str) -> pd.DataFrame:
        if auto_title:
            for df_chunk in pd.read_csv(file_path, chunksize=MAX_ROW_COUNT, header=None, dtype=str, sep=sep,
                                        skipinitialspace=True, keep_default_na=False, encoding='utf8'):
                yield df_chunk
        else:
            for df_chunk in pd.read_csv(file_path, chunksize=MAX_ROW_COUNT, dtype=str, sep=sep, skipinitialspace=True,
                                        keep_default_na=False, encoding='utf8'):
                yield df_chunk

    def _read_excel(self, file_path: str, sheet_name: str, skip_rows: int) -> pd.DataFrame:
        while True:
            df_chunk = pd.read_excel(file_path, sheet_name=sheet_name, nrows=MAX_ROW_COUNT, dtype=str,
                                     skiprows=skip_rows, header=None, keep_default_na=False)
            skip_rows = skip_rows + MAX_ROW_COUNT
            if not df_chunk.shape[0]:
                return
            else:
                yield df_chunk

    async def _read_postgres(self, date_field: str, last_date: datetime, field_info: list[Field], table: str,
                             connect_str: str, schema: str, job_num: int, version_id: uuid.UUID):
        engine = create_async_engine(connect_str)
        async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        column_name = [field.name for field in field_info]
        column_type = [field.type for field in field_info]
        cur_last_date = None
        if date_field is not None:
            column_name.append(date_field)

        async with engine.connect() as connect:
            metadata = MetaData(schema=schema)
            await connect.run_sync(metadata.reflect)
            table = Table(table, metadata, autoload_with=engine)

        table_info_name = [x.name for x in table.c]
        table_info_type = [FieldType.convert_type((x.type.python_type).__name__) for x in table.c]

        for row_i, field in enumerate(column_name):
            if field not in table_info_name:
                raise UploadDbError(f'Column with name "{field}" does not exist')
            table_type = table_info_type[table_info_name.index(field)]
            if field != date_field and FieldType[column_type[row_i]] != table_type:
                raise UploadDbError(f'Column with name "{field}" must be {column_type[row_i]}, but got {table_type} instead')
            elif field == date_field and not (table_type == FieldType.date or table_type == FieldType.datetime):
                raise UploadDbError(f'Date column with name "{field}" must be datetime or date, but got {table_type} instead')

        if date_field is None or last_date is None:
            stmt = select(func.count()).select_from(table)
        else:
            stmt = select(func.count()).where(
                or_(table.c[date_field] is None, table.c[date_field] > last_date)).select_from(table)
        async with async_session_maker() as session:
            res = await session.execute(stmt)
            row_count = res.scalar()

        for row_i in range(0, row_count, MAX_ROW_COUNT):
            if date_field is None:
                query = ",".join(column_name)
                stmt = select(text(query)).slice(row_i, row_i + MAX_ROW_COUNT).select_from(table)
            elif last_date is None:
                query = ",".join(column_name)
                stmt = select(text(query)).order_by(table.c[date_field]) \
                    .slice(row_i, row_i + MAX_ROW_COUNT).select_from(table)
            else:
                query = ",".join(column_name)
                stmt = select(text(query)) \
                    .where(or_(table.c[date_field] is None, table.c[date_field] > last_date)) \
                    .order_by(table.c[date_field]) \
                    .slice(row_i, row_i + MAX_ROW_COUNT).select_from(table)
            async with async_session_maker() as session:
                res = await session.execute(stmt)
                batch = res.all()
            if date_field is not None and row_i + MAX_ROW_COUNT >= row_count:
                for row in batch[::-1]:
                    if row[-1] is not None:
                        cur_last_date = row[-1]
                        break
            await self.upload_data_db(batch, field_info, version_id, row_i, job_num)
        return cur_last_date

    async def _read_mongo(self, date_field: str, last_date: datetime, field_info: list[Field], collection: str,
                             connect_str: str, db_name: str, job_num: int, version_id: uuid.UUID):
        client = AsyncIOMotorClient(connect_str, server_api=ServerApi('1'))
        db = client[db_name]
        collection = db[collection]
        cur_last_date = None
        key_name = [field.name for field in field_info]
        key_type = [field.type for field in field_info]
        if date_field is not None:
            key_name.append(date_field)

        for doc_i, key in enumerate(key_name):
            doc = await collection.find_one({key: {"$exists": True}})
            if doc is None:
                raise UploadDbError(f"There is not a single document with a key {key}")
            val_type = (type(doc[key])).__name__
            if key != date_field and FieldType[key_type[doc_i]] != FieldType.convert_type(val_type):
                raise UploadDbError(f'Key with name "{key}" must be {key_type[doc_i]}, but got {val_type} instead')
            if key == date_field and not (FieldType.convert_type(val_type) == FieldType.date or
                                          FieldType.convert_type(val_type) == FieldType.datetime):
                raise UploadDbError(f'Date key with name "{key}" must be date or datetime, but got {val_type} instead')

        if date_field is None or last_date is None:
            doc_count = await collection.count_documents({})
        else:
            doc_count = await collection.count_documents({"$or": [{date_field: {"$exists": False}},
                                                                  {date_field: {"$gt": last_date}}]})
        for doc_i in range(0, doc_count, MAX_ROW_COUNT):
            batch = []
            if date_field is None:
                cursor = collection.find().skip(doc_i).limit(MAX_ROW_COUNT)
            elif last_date is None:
                cursor = collection.find().sort(date_field, pymongo.ASCENDING).skip(doc_i).limit(MAX_ROW_COUNT)
            else:
                cursor = collection.find({"$or": [{date_field: {"$exists": False}}, {date_field: {"$gt": last_date}}]})\
                    .sort(date_field, pymongo.ASCENDING).skip(doc_i).limit(MAX_ROW_COUNT)
            async for doc in cursor:
                batch.append([doc[key] if key in doc else None for key in key_name])
            if date_field is not None and doc_i + MAX_ROW_COUNT >= doc_count:
                cur_last_date = batch[-1][-1]
            await self.upload_data_db(batch, field_info, version_id, doc_i, job_num)
        return cur_last_date

    async def upload_data_file(self, df_chunk: pd.DataFrame, field_info: list[Field], version_id: uuid.UUID,
                               row_num: int, job_num: int):
        column_index = [x.column_number for x in field_info]
        data: list[list] = []
        data_i = 0
        for row_i, row_val in df_chunk.iterrows():
            data.append([])
            for i, col_num in enumerate(column_index):
                field = field_info[i]
                try:
                    val = row_val[col_num].strip()
                    if val != "":
                        cast_type_service.try_cast(field.type, val)
                    data[data_i].append(val)
                except ValueError:
                    raise UploadFileError(f'Value "{row_val[col_num]}" could not be converted to the type {field.type}')
                except KeyError:
                    raise UploadFileError(f'Column with index "{col_num}" does not exist')
            data_i = data_i + 1
        current_row_num = len(data)
        rows = await self._row_service.create_bunch_row(current_row_num, row_num, version_id)
        await self._data_service.create_batch_data(data, rows, field_info, version_id, last_job=job_num)
        return

    async def upload_data_db(self, batch: list[tuple], field_info: list[Field], version_id: uuid.UUID,
                             row_num: int, job_num: int):
        current_row_num = len(batch)
        rows = await self._row_service.create_bunch_row(current_row_num, row_num, version_id)
        await self._data_service.create_batch_data(batch, rows, field_info, version_id, last_job=job_num)
        return

    async def upload_data_from_file(self, file_path: str, file_type: str, sep: str, auto_title: bool,
                                    field_info: list[Field], job_num: int) -> uuid.UUID:
        pipeline_id = field_info[0].pipeline_id
        version_id = await self._version_service.create_version(pipeline_id)
        row_number = 0
        try:
            if FileType[file_type] == FileType.csv:
                for df_chunk in self._read_csv(file_path, auto_title, sep):
                    await self.upload_data_file(df_chunk, field_info, version_id, row_number, job_num)
                    row_number = row_number + MAX_ROW_COUNT
                return version_id
            if FileType[file_type] == FileType.excel:
                sheet_name = pd.ExcelFile(file_path).sheet_names[0]
                skip_rows = 0 if auto_title else 1
                for df_chunk in self._read_excel(file_path, sheet_name, skip_rows):
                    await self.upload_data_file(df_chunk, field_info, version_id, row_number, job_num)
                    row_number = row_number + MAX_ROW_COUNT
                return version_id
        except UploadFileError as exc:
            await self._version_service.delete(version_id)
            raise UploadFileError(exc.message)
        except Exception as exc:
            await self._version_service.delete(version_id)
            raise UploadFileError(str(exc))

    async def upload_data_from_db(self, date_field: str, last_date: datetime, field_info: list[Field],
                                  connect_info: Connection, job_num: int) -> tuple[uuid.UUID, datetime]:
        pipeline_id = field_info[0].pipeline_id
        version_id = await self._version_service.create_version(pipeline_id)
        connect_str = foreign_connect_service.get_connect_str(connect_info.connect_str, connect_info.auth,
                                                              connect_info.user, connect_info.hashed_password)
        try:
            if ConnectionType[connect_info.db_type] == ConnectionType.postgresql:
                cur_last_date = await self._read_postgres(date_field, last_date, field_info, connect_info.table,
                                                          connect_str, connect_info.schema, job_num, version_id)
                return version_id, cur_last_date
            if ConnectionType[connect_info.db_type] == ConnectionType.mongodb:

                cur_last_date = await self._read_mongo(date_field, last_date, field_info, connect_info.table,
                                                       connect_str, connect_info.db_name, job_num, version_id)
                return version_id, cur_last_date
        except UploadDbError as exc:
            await self._version_service.delete(version_id)
            raise UploadDbError(str(exc))
        except Exception as exc:
            await self._version_service.delete(version_id)
            raise UploadDbError(str(exc))
