import pytest

from parser.etl import ResumeETL
from parser.config import TEST_DATA

paths = [str(i) for i in TEST_DATA.rglob("*.docx")]


@pytest.mark.parametrize("file_path", paths)
def test_parser(file_path):
    etl = ResumeETL(file_path=file_path)
    resume = etl.process()
    assert resume
