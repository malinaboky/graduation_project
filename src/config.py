from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

MAX_CONTENT_LEN = int(os.environ.get("MAX_CONTENT_LEN"))

ROOT_PATH = os.environ.get("ROOT_PATH")
TEMP_STORAGE_PATH = os.environ.get("TEMP_STORAGE_PATH")

HASH = os.environ.get("HASH")

MAX_TASK_COUNT = int(os.environ.get("MAX_TASK_COUNT"))

MAX_ROW_COUNT = int(os.environ.get("MAX_ROW_COUNT"))

MAX_CHART_COUNT = int(os.environ.get("MAX_CHART_COUNT"))

CHUNK_SIZE = int(os.environ.get("DOWNLOAD_CHUNK_SIZE"))
