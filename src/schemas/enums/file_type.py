from dataclasses import dataclass

from src.schemas.enums.base_enum import BaseEnum


@dataclass
class TypeInfo:
    extensions: list[str]


class FileType(TypeInfo, BaseEnum):
    csv = ['.csv']
    excel = ['.xls', '.xlsx']

    @classmethod
    def convert_ext_to_file_type(cls, ext: str):
        if ext in FileType.csv.extensions:
            return FileType.csv
        return FileType.excel
