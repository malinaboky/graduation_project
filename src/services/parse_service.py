import csv

from src.schemas.enums.file_type import FileType
from src.schemas.row_schema import RowInfo, ParsedRowInfo


def try_parse_row(row: str, auto: bool, sep: str) -> list[str]:
    if not auto:
        return row.split(sep)
    sep = get_delimiter(row)
    return row.split(sep)


def get_delimiter(row: str):
    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(row).delimiter
    return str(delimiter)


def get_parsed_rows(row_info: RowInfo) -> ParsedRowInfo:
    example_row = try_parse_row(row_info.example, row_info.auto_sep, row_info.sep)
    if not row_info.auto_title:
        title_row = try_parse_row(row_info.title, row_info.auto_sep, row_info.sep)
    else:
        title_row = ["Field{0}".format(x) for x in range(1, len(example_row) + 1)]
    if FileType[row_info.file_type] == FileType.csv:
        return ParsedRowInfo(example_row=example_row, title_row=[title.strip().strip(' "\'\t\r\n') for title in title_row])
    else:
        return ParsedRowInfo(example_row=example_row, title_row=title_row)
