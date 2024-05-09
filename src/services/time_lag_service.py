from src.schemas.enums.period_type import PeriodType


def generate_time_lag(period: str, period_val: int):
    if PeriodType[period] == PeriodType.day:
        return period_val * 24 * 60
    if PeriodType[period] == PeriodType.hour:
        return period_val * 60
    return period_val
