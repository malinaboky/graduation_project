import uuid

from src.schemas.enums.chart_type import ChartType, ChartDataType
from src.schemas.enums.chart_aggregation_type import ChartYAggregationType, ChartXAggregationType
from src.config import MAX_CHART_COUNT

from pydantic import BaseModel, Field, field_validator, model_validator


class ChartInfo(BaseModel):
    version: list[uuid.UUID]
    chart_type: str
    x_direct: uuid.UUID
    y_direct: uuid.UUID = Field(None)
    x_aggreg: str = Field(None)
    y_aggreg: str = Field(None)
    slice_start: int = Field(0)
    slice_end: int = Field(MAX_CHART_COUNT)

    @field_validator('chart_type')
    @classmethod
    def unsupported_chart_type(cls, v: str) -> str:
        try:
            ChartType[v]
        except KeyError:
            raise ValueError('Chart type "{0}" is unsupported'.format(v))
        return v

    @field_validator('x_aggreg')
    @classmethod
    def unsupported_x_aggregation(cls, v: str) -> str:
        try:
            ChartXAggregationType[v]
        except KeyError:
            raise ValueError('Aggregation type "{0}" is unsupported for X direction'.format(v))
        return v

    @field_validator('y_aggreg')
    @classmethod
    def unsupported_y_aggregation(cls, v: str) -> str:
        try:
            ChartYAggregationType[v]
        except KeyError:
            raise ValueError('Aggregation type "{0}" is unsupported for Y direction'.format(v))
        return v

    @model_validator(mode='after')
    def unsupported_chart_info(self) -> 'ChartInfo':
        if ChartDataType[ChartType[self.chart_type].type] == ChartDataType.one and len(self.version) > 1:
            raise ValueError(f'Only one version of data is needed for {self.chart_type}')
        if ChartDataType[ChartType[self.chart_type].type] == ChartDataType.multi and (self.y_aggreg is None or self.y_direct is None):
            raise ValueError('For multi chart y direction can not be None')
        if not ChartDataType[ChartType[self.chart_type].type] == ChartDataType.mixed and self.x_aggreg is None:
            raise ValueError('Aggregation by x can not be None')
        return self
