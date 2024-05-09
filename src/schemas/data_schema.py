import uuid

from pydantic import BaseModel


class DataSchemaAdd(BaseModel):
    field_id: uuid.UUID
    row_id: uuid.UUID
    version_id: uuid.UUID
    value: str
    last_job: int


class DataTMPSchemaAdd(BaseModel):
    version_id: uuid.UUID
    data_id: uuid.UUID
    value: str
