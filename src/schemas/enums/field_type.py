from src.schemas.enums.base_enum import BaseEnum


class FieldType(BaseEnum):
    int = "Целое число"
    float = "Вещественное число"
    complex = "Комплексное число"
    str = "Строка"
    datetime = "Дата и время"
    date = "Дата"
    time = "Время"
    bool = "Логика(0/1)"

    @classmethod
    def convert_type(cls, value):
        try:
            FieldType[value]
        except KeyError:
            return cls(FieldType.str)
        return cls(FieldType[value])
