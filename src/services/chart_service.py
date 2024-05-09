from src.schemas.chart_schema import ChartInfo
from src.schemas.enums.chart_aggregation_type import ChartXAggregationType, ChartAggregationFunc
from src.schemas.enums.chart_type import ChartType, ChartDataType
from src.schemas.enums.field_type import FieldType
from src.services.data_service import DataService
from src.services.version_service import VersionService
from src.services import cast_type_service
from src.services.field_service import FieldService


class ChartService:
    def __init__(self, data_service, field_service, version_service):
        self.data_service: DataService = data_service()
        self.field_service: FieldService = field_service()
        self.version_service: VersionService = version_service()

    async def get_batch_chart_data(self, chart_info: ChartInfo):
        result_labels = []
        data = []
        if ChartType[chart_info.chart_type].type == ChartDataType.multi.name:
            y_value_by_x = {}
            v_labels = []
            labels = []
            row_count_by_v = []
            field_y = await self.field_service.get_field(chart_info.y_direct)
            field_x = await self.field_service.get_field(chart_info.x_direct)
            for v in chart_info.version:
                y_value_by_x[v] = {}
                version = await self.version_service.get_version(v)
                v_labels.append(f'{field_y.name}: {version.name}')
                count_v = await self.data_service.get_count_x_y_data(chart_info.x_direct, chart_info.y_direct, v)
                row_count_by_v.append(count_v)
                batch = await self.data_service.get_batch_chart_x_y_data(chart_info.x_direct, chart_info.y_direct, v,
                                                                         chart_info.slice_start, chart_info.slice_end)
                for i, row in enumerate(batch):
                    if not row[0] in y_value_by_x[v]:
                        y_value_by_x[v][row[0]] = []
                        if ChartXAggregationType[chart_info.x_aggreg] == ChartXAggregationType.unique \
                                and not row[0] in labels:
                            labels.append(row[0])
                    y_value_by_x[v][row[0]].append(row[1])
                    if ChartXAggregationType[chart_info.x_aggreg] == ChartXAggregationType.all:
                        labels.append(row[0])
            for v_key in y_value_by_x:
                v_data = []
                for l_key in labels:
                    if l_key in y_value_by_x[v_key]:
                        v_data.append(ChartAggregationFunc[chart_info.y_aggreg].func(y_value_by_x[v_key][l_key],
                                                                                     field_y.type))
                    else:
                        v_data.append(0)
                    if len(result_labels) < len(labels):
                        result_labels.append(f'{field_x.name}: {l_key}')
                data.append(v_data)
            return result_labels, data, v_labels, max(row_count_by_v)
        else:
            field_x = await self.field_service.get_field(chart_info.x_direct)
            version = await self.version_service.get_version(chart_info.version[0])
            row_count = await self.data_service.get_count_x_data(chart_info.x_direct, chart_info.x_aggreg,
                                                                 chart_info.version[0])
            batch = await self.data_service.get_batch_chart_x_data(chart_info.x_direct, chart_info.x_aggreg, version.id,
                                                                   chart_info.slice_start, chart_info.slice_end)
            x_group_by_val = {}
            for val in batch:
                if val[0] not in x_group_by_val:
                    x_group_by_val[val[0]] = 0
                    result_labels.append(f'{field_x.name}: {val[0]}')
                x_group_by_val[val[0]] = x_group_by_val[val[0]] + 1
            data.append([x_group_by_val[key] for key in x_group_by_val])
            return result_labels, data, [f'{field_x.name}: {version.name}'], row_count

    async def get_batch_data_for_bubble(self, chart_info: ChartInfo):
        data = []
        data_count = {}
        data_y = []
        field_y = await self.field_service.get_field(chart_info.y_direct)
        field_x = await self.field_service.get_field(chart_info.x_direct)
        vers = await self.version_service.get_version(chart_info.version[0])
        row_count = await self.data_service.get_count_x_y_data(chart_info.x_direct, chart_info.y_direct, vers.id)
        batch = await self.data_service.get_batch_chart_x_y_data(chart_info.x_direct, chart_info.y_direct, vers.id,
                                                                 chart_info.slice_start, chart_info.slice_end)
        for row in batch:
            x = cast_type_service.try_cast(field_x.type, row[0]) if row[0] != '' else 0
            y = cast_type_service.try_cast(field_y.type, row[1]) if row[1] != '' else 0
            if f'{x}:{y}' not in data_count:
                data.append({'x': x, 'y': y})
                data_count[f'{x}:{y}'] = 1
            else:
                data_count[f'{x}:{y}'] += 1
            data_y.append(y)
        for row in data:
            row['count'] = data_count[f'{row["x"]}:{row["y"]}']
        max_val, min_val = ChartAggregationFunc.outlier.func(data_y)
        return f'{field_y.name}: {vers.name}', data, row_count, max_val, min_val
