from src.services import cast_type_service


def sum_values(values: list[str], field_type: str):
    convert_data = []
    for val in values:
        if val == "":
            convert_data.append(cast_type_service.try_cast(field_type, 0))
        else:
            convert_data.append(cast_type_service.try_cast(field_type, val))
    return sum(convert_data)


def max_value(values: list[str], field_type: str):
    convert_data = []
    for val in values:
        if val == "":
            convert_data.append(cast_type_service.try_cast(field_type, 0))
        else:
            convert_data.append(cast_type_service.try_cast(field_type, val))
    return max(convert_data)


def min_value(values: list[str], field_type: str):
    convert_data = []
    for val in values:
        if val == "":
            convert_data.append(cast_type_service.try_cast(field_type, 0))
        else:
            convert_data.append(cast_type_service.try_cast(field_type, val))
    return min(convert_data)


def average_value(values: list[str], field_type: str):
    convert_data = []
    for val in values:
        if val == "":
            convert_data.append(cast_type_service.try_cast(field_type, 0))
        else:
            convert_data.append(cast_type_service.try_cast(field_type, val))
    return sum(convert_data) / len(values)


def find_median(values):
    if len(values) % 2 == 0:
        return (values[len(values) // 2] + values[len(values) // 2 - 1]) / 2
    else:
        return values[len(values) // 2]


def outlier(values: list):
    values.sort()
    if len(values) % 2 == 0:
        median_index_q1 = len(values) // 2 - 1
        median_index_q3 = len(values) // 2
        q1 = find_median(values[:median_index_q1])
        q3 = find_median(values[median_index_q3 + 1:])
    else:
        median_index = len(values) // 2
        q1 = find_median(values[:median_index])
        q3 = find_median(values[median_index + 1:])
    intr_qr = q3 - q1
    max_val = q3 + (1.5 * intr_qr)
    min_val = q1 - (1.5 * intr_qr)
    return max_val, min_val


def count(values: list[str], field_type: str):
    return len(values)
