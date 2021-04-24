from parser import ResumeParser

parser = ResumeParser(file_path="data.docx")
sections = parser.get_content()
