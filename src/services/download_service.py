import os
import re
import shutil
import uuid
from urllib.parse import urlencode

import gdown
import pandas as pd
import requests
from fastapi import UploadFile
from requests import Response

from src.config import ROOT_PATH, CHUNK_SIZE
from src.schemas.enums.download_link import DownloadLink
from src.schemas.enums.link_type import LinkType
from src.schemas.enums.file_type import FileType
from src.schemas.form_schema import BaseFormForFile
from src.services import file_storage_service


def _check_file(data: BaseFormForFile, first_line: list[str]):
    if len(first_line) != len(data.titles):
        raise ValueError('Length of line from file is not equal to length of line from form')
    if not data.auto_title:
        if not all([first_line[x] == data.titles[x] for x in range(len(first_line))]):
            raise ValueError('Response titles do not match titles from the file')


def _get_file_extension(response):
    content_name_header = response.headers['Content-Disposition']
    _, ext = os.path.splitext(content_name_header)
    ext = ext.replace('"', '')
    if any([ext in x.extensions for x in FileType]):
        return ext
    return None


def _search_file_extension_from_google_response(response: Response):
    if response.headers["Content-Type"].startswith("text/html"):
        match = re.search("<a href=(.+)>(.+)</a>", response.text)
        if match:
            _, ext = os.path.splitext(match.groups()[1])
            if any([ext in x.extensions for x in FileType]):
                return ext
    elif "Content-Disposition" in response.headers:
        return _get_file_extension(response)
    return None


def _get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def _check_csv_file(data: BaseFormForFile, file_path: str):
    sep = data.sep if data.sep else None
    first_line = pd.read_csv(file_path, header=None, dtype=str, sep=sep, skipinitialspace=True, nrows=1).iloc[0].tolist()
    _check_file(data, first_line)


def _check_excel_file(data: BaseFormForFile, file_path: str):
    sheet_name = pd.ExcelFile(file_path).sheet_names[0]
    first_line = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1, dtype=str, header=None,
                               keep_default_na=False).iloc[0].tolist()
    _check_file(data, first_line)


def _save_big_file(download_link: str, file_path: str):
    def save_response_content(response, out_file):
        with open(out_file, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    session = requests.Session()
    response = session.get(download_link, stream=True)
    token = _get_confirm_token(response)

    if token:
        params = {'confirm': token}
        response = session.get(download_link, params=params, stream=True)

    save_response_content(response, file_path)


def get_file_from_google_drive(link: str, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> str:
    session = requests.Session()
    user_folder: str = file_storage_service.create_user_folder(user_id, ROOT_PATH)
    download_link = ""

    for link_reg in LinkType.google.regex:
        if re.match(link_reg, link):
            download_link = re.sub(link_reg, DownloadLink.google.link_reg, link)
            break
    if not download_link:
        raise ValueError("Invalid link")

    response = session.get(download_link, stream=True)
    extension = _search_file_extension_from_google_response(response)

    if not extension:
        raise ValueError("Unsupported file type")

    file_path = os.path.join(user_folder, str(pipeline_id)) + extension
    gdown.download(link, file_path, fuzzy=True)
    return file_path


def get_file_from_yandex(link: str, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> str:
    user_folder: str = file_storage_service.create_user_folder(user_id, ROOT_PATH)
    final_url = DownloadLink.yandex.link_reg + urlencode(dict(public_key=link))

    session = requests.Session()
    response_download_link = session.get(final_url)
    download_link = response_download_link.json()['href']

    download_response = session.get(download_link, stream=True)
    extension = _get_file_extension(download_response)

    if not extension:
        raise ValueError("Unsupported file type")

    file_path = os.path.join(user_folder, str(pipeline_id)) + extension
    _save_big_file(download_link, file_path)
    return file_path


def check_file(data: BaseFormForFile, file_path: str):
    _, extension = os.path.splitext(file_path)
    if extension == '.csv':
        _check_csv_file(data, file_path)
    else:
        _check_excel_file(data, file_path)


def save_file(upload_file: UploadFile, user_id: uuid.UUID, pipeline_id: uuid.UUID) -> str:
    user_folder = file_storage_service.create_user_folder(user_id, ROOT_PATH)
    _, extension = os.path.splitext(upload_file.filename)
    file_path = os.path.join(user_folder, str(pipeline_id) + extension)
    try:
        with open(file_path, "wb") as out_file:
            shutil.copyfileobj(upload_file.file, out_file)
    finally:
        upload_file.file.close()
    return file_path

