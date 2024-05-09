import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LogSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    status: str
    message: str = None
    date: datetime = datetime.utcnow().replace(second=0, microsecond=0)
