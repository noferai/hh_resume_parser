from notion_client import Client

from config import TEST_DATA, NOTION_TOKEN, NOTION_PAGE_ID
from parser.etl import ResumeETL

notion = Client(auth=NOTION_TOKEN)


with open(TEST_DATA / "<file name>", "rb") as f:
    extractor = ResumeETL(file=f)
    resume = extractor.to_notion()
    notion_resp = notion.pages.create(parent={"page_id": NOTION_PAGE_ID}, **resume)
