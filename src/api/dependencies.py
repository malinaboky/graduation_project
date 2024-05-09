from starlette.templating import Jinja2Templates

from src.services.data_service import DataService
from src.services.row_service import RowService
from src.services.upload_service import UploadService
from src.services.job_manager import JobManager
from src.services.job_type_service import JobTypeService
from src.services.pipeline_status_tracking_service import PipelineStatusTrackingService
from src.services.link_service import LinkService
from src.services.connection_service import ConnectionService
from src.services.field_service import FieldService
from src.services.pipeline_service import DataPipelineService
from src.services.running_job_service import RunningJobService
from src.services.chart_service import ChartService
from src.services.version_service import VersionService
from src.services.job_service import JobService
from src.services.file_service import FileService
from src.services.upload_user_service import UploadUserService
from src.services.log_service import LogService

from src.repositories.link_repository import LinkRepository
from src.repositories.pipeline_repository import DataPipelineRepository
from src.repositories.version_repository import VersionRepository
from src.repositories.file_repository import FileRepository
from src.repositories.connect_repository import ConnectionRepository
from src.repositories.field_repository import FieldRepository
from src.repositories.job_repository import JobRepository
from src.repositories.log_repository import LogRepository
from src.repositories.running_job_repository import RunningJobRepository
from src.repositories.data_repository import DataRepository
from src.repositories.row_repository import RowRepository


def field_service() -> FieldService:
    return FieldService(FieldRepository)


def data_pipeline_service() -> DataPipelineService:
    return DataPipelineService(DataPipelineRepository)


def version_service() -> VersionService:
    return VersionService(VersionRepository)


def chart_service() -> ChartService:
    return ChartService(data_service, field_service, version_service)


def upload_user_service() -> UploadUserService:
    return UploadUserService(data_pipeline_service, field_service, data_service, version_service)


def link_service() -> LinkService:
    return LinkService(LinkRepository)


def connection_service() -> ConnectionService:
    return ConnectionService(ConnectionRepository)


def job_service() -> JobService:
    return JobService(JobRepository)


def file_service() -> FileService:
    return FileService(FileRepository)


def log_service() -> LogService:
    return LogService(LogRepository)


def job_type_service() -> JobTypeService:
    return JobTypeService(data_service, row_service, field_service)


def running_job_service() -> RunningJobService:
    return RunningJobService(RunningJobRepository)


def job_manager() -> JobManager:
    return JobManager(data_pipeline_service, pipeline_status_tracking_service)


def row_service() -> RowService:
    return RowService(RowRepository)


def data_service() -> DataService:
    return DataService(DataRepository)


def upload_service() -> UploadService:
    return UploadService(version_service, row_service, data_service)


def pipeline_status_tracking_service() -> PipelineStatusTrackingService:
    return PipelineStatusTrackingService(data_pipeline_service, running_job_service, link_service, file_service,
                                         log_service, job_service, job_type_service, field_service, upload_service,
                                         connection_service, version_service)


templates = Jinja2Templates(directory="src/templates")
