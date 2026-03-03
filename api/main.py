import os
import hmac
import hashlib
import urllib.parse
import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.dashboard import router as dashboard_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

app.include_router(dashboard_router)

# ----------------------------
# Startup
# ----------------------------
@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


# ----------------------------
# CORS (Mini App)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://youramb.digital"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Telegram initData validation
# ----------------------------
def validate_telegram_data(init_data: str):

    parsed_data = urllib.parse.parse_qs(init_data, strict_parsing=True)

    hash_received = parsed_data.pop("hash", [None])[0]

    data_check_string = "\n".join(
        f"{k}={v[0]}" for k, v in sorted(parsed_data.items())
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

    hash_calculated = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if hash_calculated != hash_received:
        raise HTTPException(status_code=403, detail="Invalid Telegram signature")

    user_data = urllib.parse.parse_qs(init_data)["user"][0]
    user = eval(user_data)  # безопасно, т.к. подпись проверена

    return user["id"]


# ----------------------------
# Health check
# ----------------------------
@app.get("/")
async def root():
    return {"status": "API running"}