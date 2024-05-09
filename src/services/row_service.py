import uuid

from src.schemas.row_schema import RowSchemaAdd
from src.repositories.row_repository import RowRepository


class RowService:
    def __init__(self, row_repo: RowRepository):
        self.row_repo: RowRepository = row_repo()

    async def create_bunch_row(self, amount: int, start_index: int, version_id: uuid.UUID) -> list[uuid.UUID]:
        rows = [RowSchemaAdd(number=x+start_index, version_id=version_id).model_dump() for x in range(amount)]
        return await self.row_repo.add_all(rows)

    async def delete(self, id):
        return await self.row_repo.delete(id)
