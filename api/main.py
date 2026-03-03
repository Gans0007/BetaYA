import os
import hmac
import hashlib
import urllib.parse
import json
import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
app.state.pool = None


# ----------------------------
# Startup
# ----------------------------
@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)


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

    user_json = parsed_data.get("user", [None])[0]

    if not user_json:
        raise HTTPException(status_code=400, detail="User missing")

    user = json.loads(user_json)

    return user["id"]


# ----------------------------
# Dashboard endpoint
# ----------------------------
@app.post("/api/dashboard")
async def get_dashboard(data: dict):

    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    user_id = validate_telegram_data(init_data)

    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT current_streak
            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

    if not row:
        return {"streak": 0}

    return {
        "streak": row["current_streak"]
    }


@app.get("/")
async def root():
    return {"status": "API running"}