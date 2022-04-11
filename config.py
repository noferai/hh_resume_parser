import logging.config
import os
import pathlib

import sentry_sdk

PROJECT_ROOT = pathlib.Path(__file__).parent

logging.config.fileConfig(fname=PROJECT_ROOT / "logger.ini", disable_existing_loggers=False)

TEST_DATA = PROJECT_ROOT / "tests" / "data"
TG_TOKEN = os.getenv("TG_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
SENTRY_DSN = os.getenv("SENTRY_DSN")


class LanguageError(Exception):
    pass


if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=1.0)
