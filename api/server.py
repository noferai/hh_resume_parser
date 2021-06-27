import io
from typing import Optional

import uvicorn
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from parser.etl import ResumeETL

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


async def get_file(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.content


@app.get("/")
async def convert(url: Optional[str]):
    resp = await get_file(url)
    extractor = ResumeETL(file=io.BytesIO(resp))
    res = extractor.process()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
