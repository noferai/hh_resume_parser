import io
from typing import Optional

import uvicorn
import httpx
from fastapi import FastAPI
from notion_client import AsyncClient

from parser.etl import ResumeETL
from config import TG_TOKEN, NOTION_TOKEN, NOTION_PAGE_ID

app = FastAPI()
notion = AsyncClient(auth=NOTION_TOKEN)


async def send_tg_message(message: str, chat_id: int):
    API_URL = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(API_URL, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})


async def get_file(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.content


@app.get("/")
async def convert(url: Optional[str], chat_id: Optional[int]):
    resp = await get_file(url)
    extractor = ResumeETL(file=io.BytesIO(resp))
    try:
        resume = extractor.to_notion()
        notion_resp = await notion.pages.create(parent={"page_id": NOTION_PAGE_ID}, **resume)
        api_resp = notion_resp.get("url", "Notion Error")
    except Exception as e:
        api_resp = str(e)
    await send_tg_message(api_resp, chat_id)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
