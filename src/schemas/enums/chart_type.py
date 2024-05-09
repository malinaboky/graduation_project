from dataclasses import dataclass

from src.schemas.enums.base_enum import BaseEnum


class ChartDataType(BaseEnum):
    one = "one"
    multi = "multi"
    mixed = "mixed"


@dataclass
class ChartInfo:
    title: str
    type: str


class ChartType(ChartInfo, BaseEnum):
    bar_chart = "Cтолбчатая диаграмма", ChartDataType.multi.name
    pie_chart = "Круговая диаграмма", ChartDataType.one.name
    line_chart = "Линейный график", ChartDataType.multi.name
    bubble_chart = "Анализ выбросов", ChartDataType.mixed.name
