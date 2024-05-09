from dataclasses import dataclass

from src.schemas.enums.base_enum import BaseEnum


@dataclass
class LinkReg:
    link_reg: str


class DownloadLink(LinkReg, BaseEnum):
    google = r"https://drive.google.com/uc?export=download&id=\1"
    yandex = r"https://cloud-api.yandex.net/v1/disk/public/resources/download?"
    