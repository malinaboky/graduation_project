import uuid
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator, field_validator

from src.schemas.enums.db_upload_type import DbUploadType
from src.schemas.enums.field_type import FieldType
from src.schemas.enums.enum_schema import EnumInfo
from src.schemas.enums.connection_type import ConnectionType


class ConnectionInfo(BaseModel):
    db_type: str = Field(..., max_length=50)
    db_name: str = Field(..., max_length=255)
    host: str = Field(..., max_length=255)
    port: int
    table: str = Field(..., max_length=255)
    schema: str = Field(None, max_length=255)
    key: list[str] = Field(None)
    username: str = Field(None, max_length=255)
    password: str = Field(None, max_length=255)
    db_auth: str = Field(None, max_length=255)

    @field_validator('db_type')
    @classmethod
    def unsupported_db_type(cls, v: str) -> str:
        try:
            ConnectionType[v]
        except KeyError:
            raise ValueError('Database type "{0}" is unsupported'.format(v))
        return v

    @field_validator('schema')
    @classmethod
    def search_schema(cls, v: str) -> str:
        if v is None or v == "":
            return "public"
        return v

    @model_validator(mode='after')
    def db_auth_is_required(self) -> 'ConnectionInfo':
        if self.username != "" and self.password == "":
            raise ValueError('Enter the password')
        if self.password != "" and self.username == "":
            raise ValueError('Enter the username')
        if ConnectionType[self.db_type] == ConnectionType.mongodb and self.db_auth == "":
            raise ValueError('Database for auth is required for MongoDB')
        if ConnectionType[self.db_type] == ConnectionType.mongodb and (len(self.key) == 0 or not all(self.key)):
            raise ValueError('Field key can not be empty')
        return self


class FormConnectionInfo(BaseModel):
    db_type: str = Field(..., max_length=50)
    db_name: str = Field(..., max_length=255)
    host: str = Field(..., max_length=255)
    port: int
    table: str = Field(..., max_length=255)
    schema: str = Field(None, max_length=255)
    username: str = Field(None, max_length=255)
    password: str = Field(None, max_length=255)
    db_auth: str = Field(None, max_length=255)
    upload_schema: str
    date_field: str = Field(None, max_length=255)

    @field_validator('db_type')
    @classmethod
    def unsupported_db_type(cls, v: str) -> str:
        try:
            ConnectionType[v]
        except KeyError:
            raise ValueError('Database type "{0}" is unsupported'.format(v))
        return v

    @field_validator('schema')
    @classmethod
    def search_schema(cls, v: str) -> str:
        if v is None or v == "":
            return "public"
        return v

    @field_validator('upload_schema')
    @classmethod
    def unsupported_upload_schema(cls, v: str) -> str:
        try:
            DbUploadType[v]
        except KeyError:
            raise ValueError('Upload schema "{0}" is unsupported'.format(v))
        return v

    @model_validator(mode='after')
    def date_field_check(self) -> 'FormConnectionInfo':
        if DbUploadType[self.upload_schema] == DbUploadType.date_field \
                and (self.date_field is None or self.date_field == ""):
            raise ValueError('Date field is required')
        return self


class ColumnInfo:
    def __init__(self, name: str, type: EnumInfo, first_value: Any):
        self.name = name
        self.type = type

        if FieldType[type.name] == FieldType.str:
            self.first_value = str(first_value)
            if len(self.first_value) > 25:
                self.first_value = self.first_value[:25] + "..."
        else:
            self.first_value = first_value


class ConnectionSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    connect_str: str
    db_type: str
    db_name: Optional[str]
    table: str
    schema: Optional[str]
    auth: bool
    user: str = None
    hashed_password: str = None
