import logging

logging.basicConfig(format="%(asctime)s %(levelname)-5s %(message)s", level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class LanguageException(Exception):
    pass
