import os
import hmac
import hashlib
import urllib.parse
import json
import asyncpg

from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ----------------------------
# Загружаем .env
# ----------------------------
env_path = Path("/srv/bot2/.env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not loaded")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not loaded")


app = FastAPI()
app.state.pool = None


# ----------------------------
# Startup
# ----------------------------
@app.on_event("startup")
async def startup():

    print("🚀 Starting API...")
    print("📦 Connecting to PostgreSQL...")

    app.state.pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=5
    )

    print("✅ PostgreSQL connected")


# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youramb.digital"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Telegram validation
# ----------------------------
def validate_telegram_data(init_data: str):

    parsed_data = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
    hash_received = parsed_data.pop("hash", None)

    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash missing")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    hash_calculated = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if hash_calculated != hash_received:
        raise HTTPException(status_code=403, detail="Invalid Telegram signature")

    user = json.loads(parsed_data["user"])

    return user["id"]


# ----------------------------
# Подключаем роутеры
# ----------------------------
from api.dashboard import router as dashboard_router
app.include_router(dashboard_router)


# ----------------------------
# Test endpoint
# ----------------------------
@app.get("/")
async def root():
    return {"status": "API running"}