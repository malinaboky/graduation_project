from src.schemas.enums.base_enum import BaseEnum


class ConnectionType(BaseEnum):
    postgresql = "postgresql"
    mongodb = "mongodb"
