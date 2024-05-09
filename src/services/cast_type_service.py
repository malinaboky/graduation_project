import dateutil.parser as parser

from src.schemas.enums.field_type import FieldType


def try_cast(type: str, val: str):
    if FieldType[type] == FieldType.int:
        return int(val)
    if FieldType[type] == FieldType.float:
        return float(val)
    if FieldType[type] == FieldType.complex:
        return complex(val)
    if FieldType[type] == FieldType.datetime:
        return parser.parse(val)
    if FieldType[type] == FieldType.date:
        return parser.parse(val).date()
    if FieldType[type] == FieldType.time:
        return parser.parse(val).time()
    if FieldType[type] == FieldType.bool:
        return bool(val)
    return val
