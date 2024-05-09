import os
import pathlib
import uuid

from src.config import CHUNK_SIZE


def delete_file(path: str):
    file = pathlib.Path(path)
    file.unlink(missing_ok=True)


def create_user_folder(user_id: uuid.UUID, root_path: str) -> str:
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    user_folder = os.path.join(root_path, str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder


def get_path_for_user_file(user_id: uuid.UUID, root_path: str, file_name: str) -> str:
    file_path = os.path.join(root_path, str(user_id), file_name)
    return file_path


def iter_file(file_path: str):
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            yield chunk
