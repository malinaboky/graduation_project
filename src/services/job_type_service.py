import uuid
import math

from src.domain.field import Field
from src.domain.link import Link
from src.schemas.enums.field_type import FieldType
from src.services import cast_type_service
from src.schemas.enums.link_type import LinkType
from src.services import download_service
from src.services.data_service import DataService
from src.schemas.data_schema import DataTMPSchemaAdd
from src.services.row_service import RowService
from src.services.field_service import FieldService


class JobTypeService:
    def __init__(self, data_service, row_service, field_service):
        self.data_service: DataService = data_service()
        self.row_service: RowService = row_service()
        self.field_service: FieldService = field_service()

    def download(self, pipeline_id: uuid.UUID, user_id: uuid.UUID, link_info: Link):
        try:
            if LinkType[link_info.type] == LinkType.google:
                return download_service.get_file_from_google_drive(link_info.link, pipeline_id, user_id)
            if LinkType[link_info.type] == LinkType.yandex:
                return download_service.get_file_from_yandex(link_info.link, pipeline_id, user_id)
        except KeyError:
            raise KeyError("Unsupported link type")

    async def find_global_extremum(self, version_id: uuid.UUID, field: Field) -> tuple:
        min_batch_val = []
        max_batch_val = []
        cur_max = 0
        cur_min = 0
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            for i, val in enumerate(batch):
                if i == 0:
                    cur_max = cur_min = cast_type_service.try_cast(field.type, val.value)
                    continue
                cur_val = cast_type_service.try_cast(field.type, val.value)
                cur_max = cur_max if cur_val <= cur_max else cur_val
                cur_min = cur_min if cur_val >= cur_min else cur_val
            max_batch_val.append(cur_max)
            min_batch_val.append(cur_min)
        global_max = max(max_batch_val)
        global_min = min(min_batch_val)
        return global_max, global_min

    def find_median(self, values):
        if len(values) % 2 == 0:
            return (values[len(values) // 2] + values[len(values) // 2 - 1]) / 2
        else:
            return values[len(values) // 2]

    async def find_q1_q3(self, version_id: uuid.UUID, field: Field):
        total_batch = []
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            for val in batch:
                total_batch.append(cast_type_service.try_cast(field.type, val.value))
        total_batch.sort()
        if len(total_batch) % 2 == 0:
            median_index_q1 = len(total_batch) // 2 - 1
            median_index_q3 = len(total_batch) // 2
            q1 = self.find_median(total_batch[:median_index_q1])
            q3 = self.find_median(total_batch[median_index_q3 + 1:])
        else:
            median_index = len(total_batch) // 2
            q1 = self.find_median(total_batch[:median_index])
            q3 = self.find_median(total_batch[median_index + 1:])
        return q1, q3

    async def normalize(self, version_id: uuid.UUID, field: Field):
        global_max, global_min = await self.find_global_extremum(version_id, field)
        if global_max == global_min:
            return
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            update_batch = []
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                new_val = (cur_val - global_min) / (global_max - global_min)
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(new_val)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def standard(self, version_id: uuid.UUID, field: Field):
        total_sum = 0
        total_count = 0
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            total_sum = total_sum + sum([cast_type_service.try_cast(field.type, v.value) for v in batch])
            total_count = total_count + len(batch)
        if total_count == 0:
            return
        mean = total_sum / total_count
        sum_of_squares_difference = 0
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            cur_sum = sum([(cast_type_service.try_cast(field.type, v.value)-mean)**2 for v in batch])
            sum_of_squares_difference = sum_of_squares_difference + cur_sum
        standard_deviation = math.sqrt(sum_of_squares_difference / total_count)
        if standard_deviation == 0:
            return
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            update_batch = []
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                new_val = (cur_val - mean) / standard_deviation
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(new_val)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def outlier_log(self, version_id: uuid.UUID, field: Field):
        q1, q3 = await self.find_q1_q3(version_id, field)
        intr_qr = q3 - q1
        max_val = q3 + (1.5 * intr_qr)
        min_val = q1 - (1.5 * intr_qr)
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            update_batch = []
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                if cur_val < min_val or cur_val > max_val:
                    update_batch.append(DataTMPSchemaAdd(
                        version_id=version_id,
                        data_id=val.id,
                        value=str(math.log(cur_val))
                    ).model_dump())
            if len(update_batch) > 0:
                await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def outlier_set_average(self, version_id: uuid.UUID, field: Field):
        q1, q3 = await self.find_q1_q3(version_id, field)
        intr_qr = q3 - q1
        max_val = q3 + (1.5 * intr_qr)
        min_val = q1 - (1.5 * intr_qr)
        total_sum = 0
        total_count = 0
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            total_sum += sum([cast_type_service.try_cast(field.type, v.value) for v in batch])
            total_count += total_count + len(batch)
        if total_count == 0:
            return
        mean = total_sum / total_count
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            update_batch = []
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                if cur_val < min_val or cur_val > max_val:
                    update_batch.append(DataTMPSchemaAdd(
                        version_id=version_id,
                        data_id=val.id,
                        value=str(mean)
                    ).model_dump())
            if len(update_batch) > 0:
                await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def outlier_delete(self, version_id: uuid.UUID, field: Field):
        q1, q3 = await self.find_q1_q3(version_id, field)
        intr_qr = q3 - q1
        max_val = q3 + (1.5 * intr_qr)
        min_val = q1 - (1.5 * intr_qr)
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                if cur_val < min_val or cur_val > max_val:
                    await self.row_service.delete(val.row_id)
        return

    async def normalize_min_max(self, version_id: uuid.UUID, field: Field, params: dict[str, str]):
        min_val, max_val = cast_type_service.try_cast(field.type, params["min"]), \
                           cast_type_service.try_cast(field.type, params["max"])
        global_max, global_min = await self.find_global_extremum(version_id, field)
        if global_max == global_min:
            return
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            update_batch = []
            for val in batch:
                cur_val = cast_type_service.try_cast(field.type, val.value)
                new_val = min_val + (cur_val - global_min) * (max_val - min_val) / (global_max - global_min)
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(new_val)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def empty_set_min(self, version_id: uuid.UUID, field: Field):
        min_batch_val = []
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            loc_min = min(batch, key=lambda f: cast_type_service.try_cast(field.type, f.value))
            min_batch_val.append(cast_type_service.try_cast(field.type, loc_min.value))
        global_min = min(min_batch_val)
        async for batch in self.data_service.get_batch_empty_data(version_id, field.id):
            update_batch = []
            for val in batch:
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(global_min)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        return

    async def empty_set_max(self, version_id: uuid.UUID, field: Field):
        max_batch_val = []
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            loc_max = max(batch, key=lambda f: cast_type_service.try_cast(field.type, f.value))
            max_batch_val.append(cast_type_service.try_cast(field.type, loc_max.value))
        global_max = max(max_batch_val)
        async for batch in self.data_service.get_batch_empty_data(version_id, field.id):
            update_batch = []
            for val in batch:
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(global_max)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        return

    async def empty_set_average(self, version_id: uuid.UUID, field: Field):
        total_sum = 0
        total_count = 0
        async for batch in self.data_service.get_batch_full_data(version_id, field.id):
            total_sum = total_sum + sum([cast_type_service.try_cast(field.type, v.value) for v in batch])
            total_count = total_count + len(batch)
        if total_count == 0:
            return
        mean = total_sum / total_count
        async for batch in self.data_service.get_batch_empty_data(version_id, field.id):
            update_batch = []
            for val in batch:
                update_batch.append(DataTMPSchemaAdd(
                    version_id=version_id,
                    data_id=val.id,
                    value=str(mean)
                ).model_dump())
            await self.data_service.update_batch_data(version_id, update_batch)
        if FieldType[field.type] == FieldType.int:
            await self.field_service.update_field_type(field.id, FieldType.float.name)
        return

    async def empty_delete(self, version_id: uuid.UUID, field: Field):
        async for batch in self.data_service.get_batch_empty_data(version_id, field.id):
            for val in batch:
                await self.row_service.delete(val.row_id)
        return

