import json
from parser.etl import ResumeETL
from parser.config import TEST_DATA

with open(TEST_DATA / "<file name there>", "rb") as f:
    extractor = ResumeETL(file=f)
    res = extractor.process()
    print(json.dumps(res, indent=2, default=str, ensure_ascii=False))
