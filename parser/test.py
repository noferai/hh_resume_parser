import json
from parser.etl import ResumeETL

extractor = ResumeETL(file_path="../data.docx")
res = extractor.process()
print(json.dumps(res, indent=2, default=str, ensure_ascii=False))
