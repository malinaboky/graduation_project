from dataclasses import dataclass

from src.schemas.enums.base_enum import BaseEnum


@dataclass
class LinkInfo:
    title: str
    regex: list[str]


class LinkType(LinkInfo, BaseEnum):
    yandex = 'Яндекс диск', [r'https://disk.yandex.ru/d/(.*)']
    google = 'Google диск', [r'https://drive\.google\.com/file/d/(.*?)/.*?\?usp=sharing',
                             r'https://docs\.google\.com/spreadsheets/d/(.*?)/.*?\?usp=sharing']
