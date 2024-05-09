import uuid

from pydantic import ValidationError

from src.domain.field import Field
from src.schemas.field_schema import FieldInfo, FieldSchemaGetDto
from src.schemas.field_schema import FieldSchemaAdd
from src.repositories.field_repository import FieldRepository
from src.schemas.enums.field_type import FieldType


class FieldService:
    def __init__(self, field_repo: FieldRepository):
        self.field_repo: FieldRepository = field_repo()

    async def create_fields_from_db(self,
                                    pipeline_id: uuid.UUID,
                                    fields_info: list[FieldInfo]) -> dict[str, uuid.UUID]:
        fields: list[dict] = []
        for f in fields_info:
            field = FieldSchemaAdd(
                pipeline_id=pipeline_id,
                name=f.field_name,
                type=FieldType[f.type].name
            )
            fields.append(field.model_dump())
        return await self.field_repo.add_all(fields)

    async def create_fields_from_file(self,
                                      pipeline_id: uuid.UUID,
                                      titles: list[str],
                                      fields_info: list[FieldInfo]) -> dict[str, uuid.UUID]:
        fields: list[dict] = []
        for field in fields_info:
            field = FieldSchemaAdd(
                pipeline_id=pipeline_id,
                name=field.field_name,
                type=FieldType[field.type].name,
                column_number=titles.index(field.field_name)
            )
            fields.append(field.model_dump())
        return await self.field_repo.add_all(fields)

    async def get_all_fields(self, pipeline_id, is_file: bool = False):
        fields: list[Field] = await self.field_repo.find_all(pipeline_id)
        if is_file:
            fields.sort(key=lambda x: x.column_number)
        return fields

    async def get_field(self, field_id):
        field: Field = await self.field_repo.find_one(field_id)
        return field

    async def get_all_fields_dto(self, pipeline_id):
        fields: list[Field] = await self.field_repo.find_all(pipeline_id)
        res_fields = []
        for f in fields:
            if FieldType[f.type] == FieldType.int or FieldType[f.type] == FieldType.float \
                    or FieldType[f.type] == FieldType.complex:
                res_fields.append(FieldSchemaGetDto(id=f.id, name=f.name, type="num", type_name=FieldType[f.type].value))
            else:
                res_fields.append(FieldSchemaGetDto(id=f.id, name=f.name, type="str", type_name=FieldType[f.type].value))
        return res_fields

    async def update_field_type(self, id: uuid.UUID, new_type: str):
        await self.field_repo.update(id, {"type": new_type})
        return
