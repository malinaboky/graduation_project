import uuid

from pydantic import BaseModel


class FileSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    path: str
    type: str
