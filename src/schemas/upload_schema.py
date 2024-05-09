import uuid

from pydantic import BaseModel, field_validator

from src.schemas.enums.file_type import FileType


class UploadFileInfo(BaseModel):
    pipeline_id: uuid.UUID
    version: list[uuid.UUID]
    file_type: str

    @field_validator('file_type')
    @classmethod
    def unsupported_file_type(cls, v: str) -> str:
        try:
            FileType[v]
        except KeyError:
            raise ValueError(f"Unsupported file type {v}")
        return v
