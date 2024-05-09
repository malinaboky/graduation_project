from dataclasses import dataclass
from typing import List, Dict, Callable, Any
from functools import partial

from src.schemas.enums.field_type import FieldType
from src.schemas.enums.base_enum import BaseEnum


class JobGroupName(BaseEnum):
    empty: str = "Пустое значение"
    outlier: str = "Выбросы"
    other: str = "Прочее"


class Param(BaseEnum):
    min = "минимальное значение"
    max = "максимальное значение"
    old = "заменяемое значение"
    new = "замещающее значение"
    sep = "разделитель"
    auto_title = "автогенерация заголовков"
    new_format = "новый формат"
    start = "точка отсчета"
    unit_of_time = "единица измерения"


@dataclass
class ParamInfo:
    name: str
    value: str


@dataclass
class JobDetail:
    job_func: Callable[..., Any]
    field_type: List[FieldType]
    group: JobGroupName
    text: str
    params: List[Param]


class JobInfo:
    def __init__(self, name: str, title: str, params: List[ParamInfo]):
        self.name = name
        self.title = title
        self.params = params


class JobGroup:
    def __init__(self, group_name: str, jobs: List[JobInfo]):
        self.group_name = group_name
        self.jobs = jobs


class JobGroupList:
    def __init__(self, type: str, job_groups: List[JobGroup]):
        self.type = type
        self.job_list = job_groups


class JobType(JobDetail, BaseEnum):
    empty_delete = partial(lambda v_id, f, job_service: job_service.empty_delete(v_id, f)), FieldType.all(), JobGroupName.empty, "Удалить строку", []
    empty_set_min = partial(lambda v_id, f, job_service: job_service.empty_set_min(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.empty, "Заменить min значением", []
    empty_set_max = partial(lambda v_id, f, job_service: job_service.empty_set_max(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.empty, "Заменить max значением", []
    empty_set_average = partial(lambda v_id, f, job_service: job_service.empty_set_average(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.empty, "Заменить средним значением", []

    outlier_delete = partial(lambda v_id, f, job_service: job_service.outlier_delete(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.outlier, "Удалить строку", []
    outlier_log = partial(lambda v_id, f, job_service: job_service.outlier_log(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.outlier, "Логарифмировать", []
    outlier_set_average = partial(lambda v_id, f, job_service: job_service.outlier_set_average(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.outlier, "Заменить средним значением", []

    normalize = partial(lambda v_id, f, job_service: job_service.normalize(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.other, "Нормализация", []
    normalize_min_max = partial(lambda v_id, f, p, job_service: job_service.normalize(v_id, f, p)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.other, "Нормализация с диапазоном", [Param.min, Param.max]
    standard = partial(lambda v_id, f, job_service: job_service.standard(v_id, f)), [FieldType.int, FieldType.float, FieldType.complex], JobGroupName.other, "Стандартизация", []

    replace = partial(lambda x: None), [FieldType.str], JobGroupName.other, "Заменить", [Param.old, Param.new]

    datetime_reformat = partial(lambda x: None), [FieldType.datetime], JobGroupName.other, "Изменить формат", [Param.new_format]
    cal_datetime_period = partial(lambda x: None), [FieldType.datetime], JobGroupName.other, "Посчитать период", [Param.start, Param.unit_of_time]

    date_reformat = partial(lambda x: None), [FieldType.date], JobGroupName.other, "Изменить формат даты", [Param.new_format]
    cal_date_period = partial(lambda x: None), [FieldType.date], JobGroupName.other, "Посчитать период", [Param.start, Param.unit_of_time]

    time_reformat = partial(lambda x: None), [FieldType.time], JobGroupName.other, "Изменить формат времени", [Param.new_format]
    cal_time_period = partial(lambda x: None), [FieldType.time], JobGroupName.other, "Посчитать период", [Param.start, Param.unit_of_time]

    load_file = partial(lambda x: None), [], JobGroupName.other, "Загрузить файл в конвейер", [Param.sep]
    load_db = partial(lambda x: None), [], JobGroupName.other, "Загрузить бд в конвейер", []

    download = partial(lambda x, y, z, job_service: job_service.download(x, y, z)), [], JobGroupName.other, "Скачать файл", []


def _group_job_by_field_type() -> Dict[FieldType, List[JobType]]:
    type_groups = {key: [] for key in FieldType.all()}

    for key in type_groups.keys():
        for job in JobType:
            if key in job.field_type:
                type_groups[key].append(job)

    return type_groups


def _group_job_by_job_type(job_list: List[JobType]) -> Dict[JobGroupName, List[JobType]]:
    values = set(map(lambda x: x.group, job_list))
    result_dict = {key: [] for key in values}

    for key in result_dict.keys():
        for y in job_list:
            if y.group == key:
                result_dict[key].append(y)

    return result_dict


def get_all_jobs() -> List[JobGroupList]:
    jobs_grouped_by_field_type = _group_job_by_field_type()
    result_list = []

    for key in jobs_grouped_by_field_type.keys():
        jobs_grouped_by_job_type: Dict[JobGroupName, List[JobType]] = _group_job_by_job_type(jobs_grouped_by_field_type[key])
        group_list = []
        for x in jobs_grouped_by_job_type.keys():
            job_list = [JobInfo(y.name, y.text, [ParamInfo(p.name, p.value) for p in y.params]) for y in jobs_grouped_by_job_type[x]]
            group_list.append(JobGroup(x.value, job_list))
        result_list.append(JobGroupList(key.name, group_list))

    return result_list
