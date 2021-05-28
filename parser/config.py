import logging
import pathlib

logging.basicConfig(format="%(asctime)s %(levelname)-5s %(message)s", level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


PROJECT_ROOT = pathlib.Path(__file__).parent.parent
TEST_DATA = PROJECT_ROOT / "tests" / "data"


class LanguageException(Exception):
    pass
