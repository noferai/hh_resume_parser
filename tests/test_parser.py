import pytest

from config import TEST_DATA
from parser.etl import ResumeETL

paths = [str(i) for i in TEST_DATA.rglob("*.docx")]


@pytest.mark.parametrize("file_path", paths)
def test_parser(file_path):
    with open(TEST_DATA / file_path, "rb") as f:
        etl = ResumeETL(file=f)
        resume = etl.get_resume()
        assert resume
        notion = etl.to_notion()
        assert notion
