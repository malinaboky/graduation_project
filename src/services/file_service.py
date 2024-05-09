import os
import uuid

from src.domain.file import File
from src.schemas.enums.file_type import FileType
from src.schemas.file_schema import FileSchemaAdd
from src.repositories.file_repository import FileRepository


class FileService:
    def __init__(self, file_repo: FileRepository):
        self.file_repo: FileRepository = file_repo()

    async def create_file(self, pipeline_id: uuid.UUID, path: str) -> uuid.UUID:
        _, extension = os.path.splitext(path)
        file = FileSchemaAdd(
            pipeline_id=pipeline_id,
            path=path,
            type=FileType.convert_ext_to_file_type(extension).name
        )
        return await self.file_repo.add_one(file.model_dump())

    async def get_file(self, pipeline_id: uuid.UUID) -> File:
        file = await self.file_repo.find_one(pipeline_id)
        return file
