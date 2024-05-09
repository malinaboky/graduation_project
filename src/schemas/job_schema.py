import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator, Json

from src.schemas.enums.job_type import JobType


class JobInfo(BaseModel):
    name: str = Field(...)
    param: list[str] = Field(...)
    param_value: list[str] = Field(...)

    @model_validator(mode='after')
    def unsupported_job_info(self) -> 'JobInfo':
        try:
            JobType[self.name]
        except KeyError:
            raise ValueError('Job type "{0}" does not exist'.format(self.name))
        param_names = [x.name for x in JobType[self.name].params]
        for p in self.param:
            if p not in param_names:
                raise ValueError('Job "{0}" does not have param "{1}"'.format(self.name, p))
        return self


class JobSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    field_id: uuid.UUID = None
    version_id: uuid.UUID = None
    order: int
    type: str
    params: dict[str, Any] = None




