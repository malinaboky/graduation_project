from enum import Enum

from src.schemas.enums.enum_schema import EnumInfo


class BaseEnum(Enum):
    @classmethod
    def all(cls):
        return list(map(lambda c: c, cls))

    @classmethod
    def all_info(cls):
        return list(map(lambda c: EnumInfo(c.name, c), cls))
