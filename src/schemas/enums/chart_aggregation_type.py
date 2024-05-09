from dataclasses import dataclass
from functools import partial
from typing import Callable, Any

from src.schemas.enums.base_enum import BaseEnum
from src.services import aggregation_service


@dataclass
class AggregationInfo:
    title: str
    type: list[str]


@dataclass
class AggregationDetail:
    func: Callable[..., Any]


class AggregationFieldType(BaseEnum):
    num = "num"
    str = "str"


class ChartXAggregationType(BaseEnum):
    all = "Все поля"
    unique = "Уникальные поля"


class ChartYAggregationType(AggregationInfo, BaseEnum):
    sum = "Сумма", [AggregationFieldType.num.name]
    max = "Max значение", [AggregationFieldType.num.name]
    min = "Min значение", [AggregationFieldType.num.name]
    average = "Среднее значение", [AggregationFieldType.num.name]
    count = "Количество", [AggregationFieldType.num.name, AggregationFieldType.str.name]


class ChartAggregationFunc(AggregationDetail, BaseEnum):
    sum = partial(lambda v, f_type: aggregation_service.sum_values(v, f_type))
    max = partial(lambda v, f_type: aggregation_service.max_value(v, f_type))
    min = partial(lambda v, f_type: aggregation_service.min_value(v, f_type))
    average = partial(lambda v, f_type: aggregation_service.average_value(v, f_type))
    count = partial(lambda v, f_type: aggregation_service.count(v, f_type))
    outlier = partial(lambda v: aggregation_service.outlier(v))
