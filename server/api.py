import io
from typing import Optional

import uvicorn
import httpx
from fastapi import FastAPI

from parser.etl import ResumeETL
from config import TG_TOKEN, TG_CHAT_ID

app = FastAPI()


async def send_tg_message(message: str):
    API_URL = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(API_URL, json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"})


async def get_file(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.content


@app.get("/")
async def convert(url: Optional[str]):
    resp = await get_file(url)
    extractor = ResumeETL(file=io.BytesIO(resp))
    res = extractor.process()
    await send_tg_message(res["general"]["name"])


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
