import csv
import os
import uuid
import xlsxwriter

from src.services.field_service import FieldService
from src.services.data_service import DataService
from src.services.pipeline_service import DataPipelineService
from src.services.version_service import VersionService
from src.services import file_storage_service

from src.config import TEMP_STORAGE_PATH


class UploadUserService:
    def __init__(self, pipeline_service, field_service, data_service, version_service):
        self.pipeline_service: DataPipelineService = pipeline_service()
        self.field_service: FieldService = field_service()
        self.data_service: DataService = data_service()
        self.version_service: VersionService = version_service()

    async def create_csv_file(self, user_id: uuid.UUID, pipeline_id: uuid.UUID, versions: list[uuid.UUID]):
        pipeline = await self.pipeline_service.find_pipeline(pipeline_id)
        fields = await self.field_service.get_all_fields(pipeline_id, is_file=True)
        field_count = len(fields)
        user_folder = file_storage_service.create_user_folder(user_id, TEMP_STORAGE_PATH)
        file_path = os.path.join(user_folder, pipeline.name + '.csv')
        is_first = True
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            for v in versions:
                async for batch in self.data_service.get_batch_data_with_src_struct(field_count, v):
                    data = []
                    if is_first:
                        data.append([val[2] for val in batch[0:field_count]])
                        is_first = False
                    for i in range(0, len(batch), field_count):
                        data.append([val[3] for val in batch[i:i+field_count]])
                    csvwriter.writerows(data)
        return pipeline.name + '.csv'

    async def create_excel_file(self, user_id: uuid.UUID, pipeline_id: uuid.UUID, versions: list[uuid.UUID]):
        pipeline = await self.pipeline_service.find_pipeline(pipeline_id)
        fields = await self.field_service.get_all_fields(pipeline_id, is_file=True)
        field_count = len(fields)
        user_folder = file_storage_service.create_user_folder(user_id, TEMP_STORAGE_PATH)
        file_path = os.path.join(user_folder, pipeline.name + '.xlsx')
        is_first = True
        workbook = xlsxwriter.Workbook(file_path)
        for v in versions:
            row_index = 0
            version = await self.version_service.get_version(v)
            worksheet = workbook.add_worksheet(version.name)
            async for batch in self.data_service.get_batch_data_with_src_struct(field_count, v):
                if is_first:
                    worksheet.write_row(row_index, 0, [val[2] for val in batch[0:field_count]])
                    is_first = False
                    row_index += 1
                for i in range(0, len(batch), field_count):
                    worksheet.write_row(row_index, 0, [val[3] for val in batch[i:i + field_count]])
                    row_index += 1
        workbook.close()
        return pipeline.name + '.xlsx'
