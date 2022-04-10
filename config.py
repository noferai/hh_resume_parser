import logging
import os
import pathlib

import sentry_sdk

logging.basicConfig(format="%(asctime)s %(levelname)-5s %(message)s", level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

PROJECT_ROOT = pathlib.Path(__file__).parent
TEST_DATA = PROJECT_ROOT / "tests" / "data"
TG_TOKEN = os.getenv("TG_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
SENTRY_DSN = os.getenv("SENTRY_DSN")


class LanguageError(Exception):
    pass


if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=1.0)
