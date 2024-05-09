from datetime import datetime
import dateutil.parser as parser

from src.services.version_service import VersionService
from src.services.connection_service import ConnectionService
from src.schemas.enums.resource_type import ResourceType
from src.exceptions.upload_file_exception import UploadFileError
from src.services.running_job_service import RunningJobService
from src.services.upload_service import UploadService
from src.services.field_service import FieldService
from src.services.file_service import FileService
from src.services.job_type_service import JobTypeService
from src.services.log_service import LogService
from src.schemas.enums.job_type import JobType
from src.services.link_service import LinkService
from src.services.pipeline_service import DataPipelineService
from src.services.job_service import JobService
from src.schemas.pipeline_schema import PipelineSchemaTypeResGet


class PipelineStatusTrackingService:
    def __init__(self, pipeline_service, running_job_service, link_service, file_service, log_service, job_service,
                 job_type_service, field_service, upload_service, connection_service, version_service):
        self.pipeline_service: DataPipelineService = pipeline_service()
        self.running_job_service: RunningJobService = running_job_service()
        self.link_service: LinkService = link_service()
        self.log_service: LogService = log_service()
        self.job_service: JobService = job_service()
        self.job_type_service: JobTypeService = job_type_service()
        self.file_service: FileService = file_service()
        self.field_service: FieldService = field_service()
        self.upload_service: UploadService = upload_service()
        self.connection_service: ConnectionService = connection_service()
        self.version_service: VersionService = version_service()

    async def run_pipeline(self, pipeline_info: PipelineSchemaTypeResGet):
        jobs = await self.job_service.get_all_jobs_of_pipeline(pipeline_info.id)
        running_job_id = await self.running_job_service.create_running_job(pipeline_info.id, jobs[0].id)
        field_info = await self.field_service.get_all_fields(pipeline_info.id,
                                                             is_file=ResourceType[pipeline_info.type_res] != ResourceType.database)
        version_id = await self.version_service.get_last_unready_version(pipeline_info.id)
        try:
            for i, job in enumerate(jobs):
                if job.version_id == version_id and job.version_id is not None:
                    continue
                if i > 0:
                    await self.running_job_service.update(running_job_id, job.id)
                if JobType[job.type] == JobType.download:
                    link_info = await self.link_service.get_pipeline_link(pipeline_info.id)
                    file_path = JobType.download.job_func(pipeline_info.id, pipeline_info.user_id, link_info, self.job_type_service)
                    await self.file_service.create_file(pipeline_info.id, file_path)
                    continue
                elif JobType[job.type] == JobType.load_file:
                    file_info = await self.file_service.get_file(pipeline_info.id)
                    sep = str(job.params["sep"]) if "sep" in job.params else None
                    auto_title = bool(job.params["auto_title"])
                    version_id = await self.upload_service.upload_data_from_file(file_info.path, file_info.type, sep,
                                                                                 auto_title, field_info, job.order)
                    if i == 1:
                        await self.job_service.update_job(jobs[0].id, {"version_id": version_id})
                elif JobType[job.type] == JobType.load_db:
                    connect_info = await self.connection_service.get_connection(pipeline_info.id)
                    date_field = str(job.params["date_field"]) if "date_field" in job.params else None
                    last_date = parser.parse(str(job.params["last_date"])) if "last_date" in job.params else None
                    version_id, last_date = await self.upload_service.upload_data_from_db(date_field, last_date, field_info,
                                                                                          connect_info, job.order)
                    if last_date is not None:
                        update_val = {"params": {"date_field": date_field, "last_date": last_date}}
                        await self.job_service.update_job(job.id, update_val)
                else:
                    field = [f for f in field_info if f.id == job.field_id][0]
                    if len(job.params) == 0:
                        await JobType[job.type].job_func(version_id, field, self.job_type_service)
                    else:
                        await JobType[job.type].job_func(version_id, field, job.params, self.job_type_service)
                await self.job_service.update_job(job.id, {"version_id": version_id})
            await self.pipeline_service.update_pipeline_after_run(pipeline_info)
            await self.version_service.set_done(version_id)
            await self.log_service.log_ok(pipeline_info.id)
            await self.running_job_service.delete(running_job_id)
        except UploadFileError as exc:
            await self.pipeline_service.set_on_pause(pipeline_info.id)
            await self.running_job_service.delete(running_job_id)
            await self.log_service.log_error(pipeline_info.id, exc.message[0:255])
        except Exception as exc:
            await self.pipeline_service.set_on_pause(pipeline_info.id)
            await self.running_job_service.delete(running_job_id)
            await self.log_service.log_error(pipeline_info.id, str(exc)[0:255])

