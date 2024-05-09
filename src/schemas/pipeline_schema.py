import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PipelineSchemaGet(BaseModel):
    id: uuid.UUID
    name: str
    pause: bool


class PipelineSchemaAdd(BaseModel):
    user_id: uuid.UUID
    name: str = Field(..., max_length=255)
    pause: bool = False
    min_time_lag: int = None
    type_res: str


class PipelineSchemaUpdate(BaseModel):
    pause: bool = False
    date: datetime


class PipelineSchemaTypeResGet(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type_res: str
