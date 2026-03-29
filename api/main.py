import os
import hmac
import hashlib
import urllib.parse
import json

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
from core.database import create_pool

@app.on_event("startup")
async def startup():

    print("🚀 Starting API...")
    print("📦 Connecting to PostgreSQL...")

    await create_pool()

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
# Подключаем роутеры
# ----------------------------
from api.dashboard import router as dashboard_router
from api.profile import router as profile_router
from api.settings import router as settings_router

app.include_router(dashboard_router)
app.include_router(profile_router)
app.include_router(settings_router)

# ----------------------------
# Test endpoint
# ----------------------------
@app.get("/")
async def root():
    return {"status": "API running"}