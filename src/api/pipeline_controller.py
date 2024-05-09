import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Request, Body, File
from fastapi.responses import StreamingResponse

from src.config import MAX_CONTENT_LEN

from src.auth.auth_service import current_active_user
from src.domain.user import User

from src.middlewares.dependencies import ContentTypeChecker, ContentLenChecker

from src.schemas.enums.resource_type import ResourceType
from src.schemas.enums.link_type import LinkType
from src.schemas.enums.file_type import FileType
from src.schemas.enums.period_type import PeriodType
from src.schemas.enums.field_type import FieldType
from src.schemas.enums.job_type import get_all_jobs
from src.schemas.enums.chart_type import ChartType
from src.schemas.enums.chart_aggregation_type import ChartXAggregationType, ChartYAggregationType

from src.schemas.form_schema import FormForFile, FormForLink, FormForDB
from src.schemas.connection_schema import ConnectionInfo
from src.schemas.row_schema import RowInfo
from src.schemas.chart_schema import ChartInfo
from src.schemas.upload_schema import UploadFileInfo

from src.services.link_service import LinkService
from src.services.field_service import FieldService
from src.services.upload_user_service import UploadUserService
from src.services.pipeline_service import DataPipelineService
from src.services.job_service import JobService
from src.services.mime_mapping import mimetypes
from src.services.file_service import FileService
from src.services.log_service import LogService
from src.services.connection_service import ConnectionService
from src.services.version_service import VersionService
from src.services.chart_service import ChartService
from src.services import parse_service, foreign_connect_service, download_service, file_storage_service

from src.api.dependencies import templates
from src.api.dependencies import data_pipeline_service, field_service, link_service
from src.api.dependencies import job_service, file_service, log_service, chart_service
from src.api.dependencies import connection_service, version_service, upload_user_service

from src.config import TEMP_STORAGE_PATH

router = APIRouter(
    prefix="/pipelines",
    tags=["pipelines"],
)


@router.post("/parse", dependencies=[Depends(current_active_user)])
async def try_parse_rows(
        row_info: RowInfo
):
    parsed_rows = parse_service.get_parsed_rows(row_info)
    field_types = FieldType.all()
    html = templates.env.get_template("create-page/table-panel.html").render(parsed=parsed_rows, types=field_types)
    return {"html": html}


@router.post("/connect", dependencies=[Depends(current_active_user)])
async def try_to_connect(
        connect_info: ConnectionInfo
):
    columns = await foreign_connect_service.try_to_connect(connect_info)
    html = templates.env.get_template("create-page/db-table-panel.html").render(columns=columns)
    return {"html": html}


@router.get("/jobs", dependencies=[Depends(current_active_user)])
async def get_jobs_info():
    job_list = get_all_jobs()
    link_types = LinkType.all_info()
    file_types = FileType.all_info()
    return {"jobs": job_list, "links": link_types, "files": file_types}


@router.get("/info/{pipeline}", dependencies=[Depends(current_active_user)])
async def get_pipeline_info(
        pipeline: uuid.UUID,
        field_service: Annotated[FieldService, Depends(field_service)],
        version_service: Annotated[VersionService, Depends(version_service)]):
    versions = await version_service.get_done_version(pipeline)
    fields = await field_service.get_all_fields_dto(pipeline)
    charts = ChartType.all_info()
    chart_x = ChartXAggregationType.all_info()
    chart_y = ChartYAggregationType.all_info()
    return {"versions": versions, "fields": fields, "charts": charts, "chartX": chart_x, "chartY": chart_y}


@router.post("/chart", dependencies=[Depends(current_active_user)])
async def get_data_for_chart(
        chart_info: ChartInfo,
        chart_service: Annotated[ChartService, Depends(chart_service)]):
    if ChartType[chart_info.chart_type] == ChartType.bubble_chart:
        label, data, count, max_val, min_val = await chart_service.get_batch_data_for_bubble(chart_info)
        return {"label": label, "data": data, "count": count, "max": max_val, "min": min_val}
    else:
        labels, data, versions, row_count = await chart_service.get_batch_chart_data(chart_info)
        return {"labels": labels, "data": data, "versions": versions, "count": row_count}


@router.post("/file", dependencies=[Depends(current_active_user),
                                    Depends(ContentLenChecker(content_len=MAX_CONTENT_LEN)),
                                    Depends(ContentTypeChecker([mimetypes.types_map['.csv'],
                                                                mimetypes.types_map['.xls'],
                                                                mimetypes.types_map['.xlsx']]))])
async def create_pipeline_from_file(
        pipeline_service: Annotated[DataPipelineService, Depends(data_pipeline_service)],
        field_service: Annotated[FieldService, Depends(field_service)],
        job_service: Annotated[JobService, Depends(job_service)],
        file_service: Annotated[FileService, Depends(file_service)],
        log_service: Annotated[LogService, Depends(log_service)],
        user: User = Depends(current_active_user),
        data: FormForFile = Body(...),
        file: UploadFile = File(...)
):
    pipeline_id = await pipeline_service.create_pipeline(data.name, ResourceType.file.name, user.id)
    path = download_service.save_file(file, user.id, pipeline_id)

    try:
        download_service.check_file(data, path)
    except ValueError as exc:
        await pipeline_service.delete(pipeline_id)
        file_storage_service.delete_file(path)
        raise ValueError(exc)

    await file_service.create_file(pipeline_id, path)
    fields_info = await field_service.create_fields_from_file(pipeline_id, data.titles, data.field_job)
    await job_service.create_jobs_for_file(pipeline_id, data.sep, data.auto_title, data.field_job, fields_info, False)
    await log_service.log_ok(pipeline_id)
    return


@router.post("/link")
async def create_pipeline_from_link(
        pipeline_service: Annotated[DataPipelineService, Depends(data_pipeline_service)],
        field_service: Annotated[FieldService, Depends(field_service)],
        link_service: Annotated[LinkService, Depends(link_service)],
        job_service: Annotated[JobService, Depends(job_service)],
        log_service: Annotated[LogService, Depends(log_service)],
        user: User = Depends(current_active_user),
        data: FormForLink = Body(...)
):
    pipeline_id = await pipeline_service.create_pipeline(data.name, ResourceType.link.name, user.id, data.period, data.period_value)
    await link_service.create_link(pipeline_id, data.link, data.link_type)
    fields_info = await field_service.create_fields_from_file(pipeline_id, data.titles, data.field_job)
    await job_service.create_jobs_for_file(pipeline_id, data.sep, data.auto_title, data.field_job, fields_info)
    await log_service.log_ok(pipeline_id)
    return


@router.post("/database")
async def create_pipeline_from_db(
        pipeline_service: Annotated[DataPipelineService, Depends(data_pipeline_service)],
        connection_service: Annotated[ConnectionService, Depends(connection_service)],
        field_service: Annotated[FieldService, Depends(field_service)],
        job_service: Annotated[JobService, Depends(job_service)],
        log_service: Annotated[LogService, Depends(log_service)],
        user: User = Depends(current_active_user),
        data: FormForDB = Body(...)
):
    pipeline_id = await pipeline_service.create_pipeline(data.name, ResourceType.database.name, user.id, data.period, data.period_value)
    await connection_service.create_connection(pipeline_id, data)
    fields_info = await field_service.create_fields_from_db(pipeline_id, data.field_job)
    await job_service.create_jobs_for_db(pipeline_id, data.field_job, fields_info, data.date_field)
    await log_service.log_ok(pipeline_id)
    return


@router.get("/add", dependencies=[Depends(current_active_user)])
async def get_pipeline_form(request: Request):
    period_types = PeriodType.all_info()
    link_types = LinkType.all_info()
    return templates.TemplateResponse(request=request, name="create-page/create-page.html",
                                      context={"periods": period_types, "links": link_types})


@router.get("")
async def get_all_pipelines(
        request: Request,
        data_pipeline_service: Annotated[DataPipelineService, Depends(data_pipeline_service)],
        log_service: Annotated[LogService, Depends(log_service)],
        user: User = Depends(current_active_user)):
    nickname = user.email
    pipelines = await data_pipeline_service.get_user_pipelines(user.id)
    logs = await log_service.get_last_log([p.id for p in pipelines])
    return templates.TemplateResponse(request=request, name="main-page/main-page.html",
                                      context={"nickname": nickname, "pipelines": pipelines, "logs": logs})


@router.get("/stat/{pipeline}", dependencies=[Depends(current_active_user)])
async def get_pipeline_stat(
        request: Request,
        pipeline: uuid.UUID,
        version_service: Annotated[VersionService, Depends(version_service)]):
    versions = await version_service.get_all_version(pipeline)
    return templates.TemplateResponse(request=request, name="stat-page/stat-page.html",
                                      context={"versions": versions})


@router.get("/download/{file_name}")
async def download_pipeline_data(request: Request, file_name: str, user: User = Depends(current_active_user)):
    file_path = file_storage_service.get_path_for_user_file(user.id, TEMP_STORAGE_PATH, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return StreamingResponse(file_storage_service.iter_file(file_path), headers=headers, media_type='text/csv')


@router.post("/download")
async def download_pipeline_data(
        request: Request,
        upload_info: UploadFileInfo,
        upload_service: Annotated[UploadUserService, Depends(upload_user_service)],
        user: User = Depends(current_active_user)):
    if FileType[upload_info.file_type] == FileType.csv:
        file_name = await upload_service.create_csv_file(user.id, upload_info.pipeline_id, upload_info.version)
    else:
        file_name = await  upload_service.create_excel_file(user.id, upload_info.pipeline_id, upload_info.version)
    return {'file': file_name}
