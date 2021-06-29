import pytest

from parser.etl import ResumeETL
from config import TEST_DATA

paths = [str(i) for i in TEST_DATA.rglob("*.docx")]


@pytest.mark.parametrize("file_path", paths)
def test_parser(file_path):
    with open(TEST_DATA / file_path, "rb") as f:
        etl = ResumeETL(file=f)
        resume = etl.get_resume()
        assert resume
