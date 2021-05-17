from parser.etl import ResumeETL

extractor = ResumeETL(file_path="../data.docx")
extractor.process()
s = ""
