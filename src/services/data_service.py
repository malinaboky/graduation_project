import asyncio
import uuid

from src.domain.data import Data
from src.config import MAX_ROW_COUNT
from src.domain.field import Field
from src.schemas.data_schema import DataSchemaAdd
from src.schemas.enums.chart_aggregation_type import ChartXAggregationType
from src.repositories.data_repository import DataRepository


class DataService:
    def __init__(self, data_repo: DataRepository):
        self.data_repo: DataRepository = data_repo()

    async def create_batch(self, values: list[list], rows: list[uuid.UUID], field_id: uuid.UUID, field_i: int,
                           version_id: uuid.UUID, last_job: int):
        data = []
        for row_i, row_val in enumerate(values):
            data.append(DataSchemaAdd(
                field_id=field_id,
                row_id=rows[row_i],
                version_id=version_id,
                value=str(row_val[field_i]) if row_val[field_i] is not None else "",
                last_job=last_job
            ).model_dump())
            if len(data) * 6 >= MAX_ROW_COUNT * 3:
                await self.data_repo.add_all(data)
                data = []
            elif row_i == len(values) - 1:
                await self.data_repo.add_all(data)
        return

    async def create_batch_data(self, values: list[list], rows: list[uuid.UUID], fields: list[Field],
                                version_id: uuid.UUID, last_job: int):
        tasks = [asyncio.create_task(
            self.create_batch(values, rows, field.id, field_i, version_id, last_job))
            for field_i, field in enumerate(fields)]
        await asyncio.wait(tasks)
        return

    async def get_batch_data(self, version_id: uuid.UUID, field_id: uuid.UUID) -> list[Data]:
        data_num = 0
        data_num = await self.data_repo.count_data_by_field(version_id, field_id)
        for i in range(0, data_num, MAX_ROW_COUNT):
            batch = await self.data_repo.get_batch_data(version_id, field_id, i)
            yield batch

    async def get_batch_data_with_src_struct(self, field_count: int, version_id: uuid.UUID) -> list[Data]:
        data_num = await self.data_repo.count_data_by_version(version_id)
        limit = MAX_ROW_COUNT // field_count * field_count
        for i in range(0, data_num, limit):
            batch = await self.data_repo.get_batch_data_with_src_struct(version_id, i, limit)
            yield batch

    async def get_batch_full_data(self, version_id: uuid.UUID, field_id: uuid.UUID) -> list[Data]:
        data_num = 0
        data_num = await self.data_repo.count_full_data_by_field(version_id, field_id)
        for i in range(0, data_num, MAX_ROW_COUNT):
            batch = await self.data_repo.get_batch_full_data(version_id, field_id, i)
            yield batch

    async def get_batch_empty_data(self, version_id: uuid.UUID, field_id: uuid.UUID) -> list[Data]:
        data_num = 0
        data_num = await self.data_repo.count_empty_data_by_field(version_id, field_id)
        for i in range(0, data_num, MAX_ROW_COUNT):
            batch = await self.data_repo.get_batch_empty_data(version_id, field_id, i)
            yield batch

    async def get_batch_chart_x_y_data(self, x_direct: uuid.UUID, y_direct: uuid.UUID, version_id: uuid.UUID,
                                       start: int, end: int) -> list[tuple]:
        batch = await self.data_repo.get_batch_for_x_y(x_direct, y_direct, version_id, start, end)
        return batch

    async def get_batch_chart_x_data(self, x_direct: uuid.UUID, x_aggreg: str, version_id: uuid.UUID,
                                       start: int, end: int) -> list[tuple]:
        if ChartXAggregationType[x_aggreg] == ChartXAggregationType.all:
            batch = await self.data_repo.get_batch_for_x_all(x_direct, version_id, start, end)
        else:
            batch = await self.data_repo.get_batch_for_x_unique(x_direct, version_id, start, end)
        return batch

    async def get_count_x_y_data(self, x_direct: uuid.UUID, y_direct: uuid.UUID, version_id: uuid.UUID) -> int:
        count = await self.data_repo.count_for_x_y(x_direct, y_direct, version_id)
        return count

    async def get_count_x_data(self, x_direct: uuid.UUID, x_aggreg: str, version_id: uuid.UUID) -> int:
        if ChartXAggregationType[x_aggreg] == ChartXAggregationType.all:
            count = await self.data_repo.count_for_x_all(x_direct, version_id)
        else:
            count = await self.data_repo.count_for_x_unique(x_direct, version_id)
        return count

    async def update_batch_data(self, version_id: uuid.UUID, new_val: list[dict]):
        if len(new_val) == MAX_ROW_COUNT:
            first_new_val = new_val[:MAX_ROW_COUNT // 2]
            second_new_val = new_val[MAX_ROW_COUNT // 2:]
            await self.data_repo.update_batch_data(version_id, first_new_val)
            await self.data_repo.update_batch_data(version_id, second_new_val)
        else:
            await self.data_repo.update_batch_data(version_id, new_val)
        return
