from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from sqlalchemy import select, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.schemas.enums.enum_schema import EnumInfo
from src.schemas.enums.field_type import FieldType
from src.schemas.connection_schema import ConnectionInfo, ColumnInfo
from src.schemas.enums.connection_type import ConnectionType
from src.services import crypt_service


def create_postgres_connect_str(username: str, password: str, host: str, port: int, db_name: str):
    if username == "":
        return f"postgresql+asyncpg://{host}:{port}/{db_name}"
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"


def crate_mongo_connect_str(username: str, password: str, host: str, port: int, auth_db: str):
    if username == "":
        return f"mongodb://{host}:{port}/{auth_db}"
    return f"mongodb://{username}:{password}@{host}:{port}/{auth_db}"


def get_connect_str(connect_str: str, auth: bool, username: str, password: str):
    if auth:
        return connect_str.replace("<user>", username).replace("<pass>", crypt_service.decrypt(password).decode('UTF-8'))
    return connect_str.replace("<user>:<pass>@", "")


async def try_to_connect_to_postgresql(info: ConnectionInfo):
    db_url = create_postgres_connect_str(info.username, info.password, info.host, info.port, info.db_name)

    engine = create_async_engine(db_url)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    column_info: list[tuple]
    first_row: list[str]

    async with engine.connect() as connect:
        metadata = MetaData(schema=info.schema)
        await connect.run_sync(metadata.reflect)
        table = Table(info.table, metadata, autoload_with=engine)
        column_info = [(x.name, FieldType.convert_type((x.type.python_type).__name__)) for x in table.c]

    async with async_session_maker() as session:
        stmt = select(table).limit(1)
        res = await session.execute(stmt)
        first_row = res.first()

    if not first_row:
        first_row = ["-" for _ in range(len(column_info))]

    result = [ColumnInfo(
        name=column_info[x][0],
        type=EnumInfo(name=column_info[x][1].name, value=column_info[x][1].value),
        first_value=first_row[x]) for x in range(len(column_info))]

    return result


async def try_to_connect_to_mongodb(info: ConnectionInfo):
    key_info = {}

    db_url = crate_mongo_connect_str(info.username, info.password, info.host, info.port, info.db_auth)
    client = AsyncIOMotorClient(db_url, server_api=ServerApi('1'))
    db = client[info.db_name]
    collection = db[info.table]

    for key in info.key:
        doc = await collection.find_one({key: {"$exists": True}})
        if doc is None:
            raise ValueError(f"There is not a single document with a key {key}")
        key_info[key] = FieldType.convert_type((type(doc[key])).__name__)

    doc = await collection.find_one({info.key[0]: {"$exists": True}})

    result = [ColumnInfo(
        name=key,
        first_value=doc[key] if key in doc else "-",
        type=val) for key, val in key_info.items()]

    return result


async def try_to_connect(connect_info: ConnectionInfo) -> list[ColumnInfo]:
    columns = None
    if ConnectionType[connect_info.db_type] == ConnectionType.postgresql:
        columns = await try_to_connect_to_postgresql(connect_info)
    if ConnectionType[connect_info.db_type] == ConnectionType.mongodb:
        columns = await try_to_connect_to_mongodb(connect_info)
    return columns
