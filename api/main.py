import os
import hmac
import hashlib
import urllib.parse
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

pool = None


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
# Dashboard endpoint
# ----------------------------
@app.post("/api/dashboard")
async def dashboard(data: dict):

    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="Missing initData")

    user_id = validate_telegram_data(init_data)

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            """
            SELECT user_id, xp, current_streak, league
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

    if not user:
        return {"error": "User not found"}

    return {
        "xp": user["xp"],
        "streak": user["current_streak"],
        "league": user["league"],
        "weekly_xp": [50, 80, 120, 200, 260, 350, 480]  # позже сделаем реальный расчёт
    }


# ----------------------------
# Health check
# ----------------------------
@app.get("/")
async def root():
    return {"status": "API running"}