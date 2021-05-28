import json
from parser.etl import ResumeETL
from parser.config import TEST_DATA

extractor = ResumeETL(file_path=TEST_DATA / "Павел Скориков.docx")
res = extractor.process()
print(json.dumps(res, indent=2, default=str, ensure_ascii=False))
