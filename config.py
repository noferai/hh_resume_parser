import os
import logging
import pathlib

logging.basicConfig(format="%(asctime)s %(levelname)-5s %(message)s", level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).parent
TEST_DATA = PROJECT_ROOT / "tests" / "data"
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")


class LanguageException(Exception):
    pass
