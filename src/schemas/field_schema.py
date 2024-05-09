import uuid
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator

from src.schemas.enums.field_type import FieldType
from src.schemas.enums.job_type import JobType
from src.schemas.job_schema import JobInfo


class FieldInfo(BaseModel):
    field_name: str = Field(...)
    type: str = Field(...)
    job_list: List[JobInfo] = Field(...)

    @field_validator('type')
    @classmethod
    def unsupported_field_type(cls, v: str) -> str:
        try:
            FieldType[v]
        except KeyError:
            raise ValueError('Field type "{0}" is unsupported data type'.format(v))
        return v

    @model_validator(mode='after')
    def unsupported_field_info(self) -> 'FieldInfo':
        for job in self.job_list:
            if FieldType[self.type] not in JobType[job.name].field_type:
                raise ValueError('Job "{0}" is unsupported for {1} data type'.format(job, FieldType[self.type]))
        return self


class FieldSchemaAdd(BaseModel):
    pipeline_id: uuid.UUID
    name: str = Field(..., max_length=255)
    type: str
    column_number: int = None


class FieldSchemaGet(BaseModel):
    id: uuid.UUID
    name: str


class FieldSchemaGetDto(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    type_name: str
