import uuid
from datetime import datetime

from pydantic import BaseModel


class VersionSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    number: int = 0
    is_done: bool = False
    date: datetime = datetime.utcnow().replace(second=0, microsecond=0)


class VersionSchema(BaseModel):
    pipeline_id: uuid.UUID
    number: int
    is_done: bool
    date: datetime


class VersionInfo(BaseModel):
    id: uuid.UUID
    is_done: bool
    name: str
