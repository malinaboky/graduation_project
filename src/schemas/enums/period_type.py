from dataclasses import dataclass

from src.schemas.enums.base_enum import BaseEnum


@dataclass
class PeriodDetail:
    title: str
    min: int
    max: int


class PeriodType(PeriodDetail, BaseEnum):
    day = "Дни", 1, 180
    hour = "Часы", 1, 180 * 60
    min = "Минуты", 30, 180 * 30 * 60

