import uuid

from pydantic import BaseModel, model_validator, field_validator

from src.schemas.enums.file_type import FileType


class RowInfo(BaseModel):
    file_type: str
    auto_title: bool
    title: str = None
    example: str
    auto_sep: bool
    sep: str = None

    @model_validator(mode='after')
    def if_auto_false_not_none(self) -> 'RowInfo':
        if not self.example or len(self.example.replace(' ', '')) == 0:
            raise ValueError('The example string can not be empty')
        if not self.auto_title:
            if not self.title:
                raise ValueError("The title string can not be empty")
            if len(self.title.replace(' ', '')) == 0:
                raise ValueError("The title string can not be empty")
        if not self.auto_sep:
            if not self.sep:
                raise ValueError("Separator can not be empty")
        return self

    @field_validator('file_type')
    @classmethod
    def unsupported_file_type(cls, v: str) -> str:
        try:
            FileType[v]
        except KeyError:
            raise ValueError(f"Unsupported file type {v}")
        return v


class ParsedRowInfo(BaseModel):
    title_row: list[str]
    example_row: list[str]

    @model_validator(mode='after')
    def if_auto_false_title_not_none(self) -> 'ParsedRowInfo':
        if len(self.title_row) != len(self.example_row):
            raise ValueError("The number of title must be equal to the number of examples")
        return self

    @field_validator('title_row')
    @classmethod
    def all_titles_must_be_different(cls, v: list[str]) -> list[str]:
        title_set: set = set(v)
        if len(title_set) != len(v):
            raise ValueError("All titles must be different")
        return v


class RowSchemaAdd(BaseModel):
    version_id: uuid.UUID
    number: int
