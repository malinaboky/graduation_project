import uuid

from src.domain.connection import Connection
from src.schemas.enums.connection_type import ConnectionType
from src.services import crypt_service
from services.foreign_connect_service import create_postgres_connect_str, crate_mongo_connect_str
from src.schemas.form_schema import FormForDB
from src.repositories.connect_repository import ConnectionRepository
from src.schemas.connection_schema import ConnectionSchemaAdd


class ConnectionService:
    def __init__(self, connect_repo: ConnectionRepository):
        self.connect_repo: ConnectionRepository = connect_repo()

    async def create_connection(self, pipeline_id: uuid.UUID, connect_info: FormForDB) -> uuid.UUID:
        connect_url: str
        if ConnectionType[connect_info.db_type] == ConnectionType.postgresql:
            connect_url = create_postgres_connect_str("<user>", "<pass>", connect_info.host, connect_info.port,
                                                      connect_info.db_name)
        else:
            connect_url = crate_mongo_connect_str("<user>", "<pass>", connect_info.host, connect_info.port,
                                                  connect_info.db_auth)
        connect: ConnectionSchemaAdd
        if connect_info.username != "":
            connect = ConnectionSchemaAdd(
                pipeline_id=pipeline_id,
                connect_str=connect_url,
                db_type=connect_info.db_type,
                db_name=connect_info.db_name,
                schema=connect_info.schema if ConnectionType[connect_info.db_type] == ConnectionType.postgresql else None,
                table=connect_info.table,
                auth=True,
                user=connect_info.username,
                hashed_password=crypt_service.encrypt_str(connect_info.password)
            )
        else:
            connect = ConnectionSchemaAdd(
                pipeline_id=pipeline_id,
                connect_str=connect_url,
                db_type=connect_info.db_type,
                schema=connect_info.schema if ConnectionType[
                                                  connect_info.db_type] == ConnectionType.postgresql else None,
                db_name=connect_info.db_name,
                table=connect_info.table,
                auth=False
            )
        return await self.connect_repo.add_one(connect.model_dump())

    async def get_connection(self, pipeline_id: uuid.UUID) -> Connection:
        connect = await self.connect_repo.find_one(pipeline_id)
        return connect
