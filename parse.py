import json
from notion_client import Client

from parser.etl import ResumeETL
from config import TEST_DATA, NOTION_TOKEN, NOTION_PAGE_ID


notion = Client(auth=NOTION_TOKEN)


with open(TEST_DATA / "<file name>", "rb") as f:
    extractor = ResumeETL(file=f)
    resume = extractor.to_notion()
    # print(json.dumps(resume, indent=2, default=str, ensure_ascii=False))
    notion_resp = notion.pages.create(parent={"page_id": NOTION_PAGE_ID}, **resume)
    # print(notion_resp)
