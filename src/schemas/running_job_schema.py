import uuid

from pydantic import BaseModel


class RunningJobSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    job_id: uuid.UUID
