import uuid

from pydantic import BaseModel


class LinkSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    link: str
    type: str
