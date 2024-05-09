import json
import re
from typing import List

from pydantic import BaseModel, Field, model_validator, field_validator

from src.schemas.connection_schema import FormConnectionInfo
from src.schemas.enums.link_type import LinkType
from src.schemas.enums.period_type import PeriodType
from src.schemas.field_schema import FieldInfo


class BaseForm(BaseModel):
    name: str = Field(..., max_length=255)
    field_job: List[FieldInfo] = Field(...)


class BaseFormForFile(BaseModel):
    auto_sep: bool = Field(...)
    auto_title: bool = Field(...)
    titles: List[str] = Field(...)
    example: str = Field(...)

    sep: str = Field(None, max_length=20)

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class TimeInfo(BaseModel):
    period: str = Field(..., max_length=255)
    period_value: int = Field(...)

    @field_validator('period')
    @classmethod
    def unsupported_period_type(cls, v: str) -> str:
        try:
            PeriodType[v]
        except KeyError:
            raise ValueError('Period type "{0}" is unsupported'.format(v))
        return v

    @model_validator(mode='after')
    def time_gone_out_of_bounds(self) -> 'TimeInfo':
        if int(PeriodType[self.period].min) <= self.period_value <= int(PeriodType[self.period].max):
            return self
        raise ValueError('Time has gone out of bounds')


class FormForFile(BaseForm, BaseFormForFile, BaseModel):
    pass


class FormForLink(BaseForm, BaseFormForFile, TimeInfo, BaseModel):
    link_type: str = Field(..., max_length=10)
    link: str = Field(..., max_length=300)

    @field_validator('link_type')
    @classmethod
    def unsupported_link_type(cls, v: str) -> str:
        try:
            LinkType[v]
        except KeyError:
            raise ValueError('Link type "{0}" is unsupported'.format(v))
        return v

    @model_validator(mode='after')
    def invalid_link(self) -> 'FormForLink':
        if any([re.match(reg, self.link) for reg in LinkType[self.link_type].regex]):
            return self
        raise ValueError('Invalid link')


class FormForDB(BaseForm, FormConnectionInfo, TimeInfo, BaseModel):
    pass
