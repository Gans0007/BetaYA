from fastapi import APIRouter, Request
from core.database import get_pool
from api.telegram_auth import validate_telegram_data

router = APIRouter(prefix="/api/settings")

VALID_TONES = ["friend", "gamer", "spartan"]

VALID_TIMEZONES = [
    "Europe/Kyiv",
    "Europe/Berlin",
    "Europe/Warsaw",
    "America/Vancouver",
    "Europe/Moscow"
]


# =====================================================
# 🔹 ПОЛУЧИТЬ НАСТРОЙКИ
# =====================================================
@router.post("")
async def get_settings(request: Request):
    data = await request.json()
    init_data = data.get("initData")

    if not init_data:
        return {"ok": False, "error": "no initData"}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT notification_tone, timezone, share_confirmation_media
            FROM users
            WHERE user_id = $1
        """, user_id)

    if not row:
        return {"ok": False, "error": "user not found"}

    return {
        "ok": True,
        "tone": row["notification_tone"],
        "timezone": row["timezone"],
        "share_on": row["share_confirmation_media"]
    }


# =====================================================
# 🔹 СМЕНА ТОНА
# =====================================================
@router.post("/tone")
async def set_tone(request: Request):
    data = await request.json()
    init_data = data.get("initData")
    tone = data.get("tone")

    if not init_data or tone not in VALID_TONES:
        return {"ok": False}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET notification_tone = $1
            WHERE user_id = $2
        """, tone, user_id)

    return {"ok": True, "tone": tone}


# =====================================================
# 🔹 СМЕНА TIMEZONE
# =====================================================
@router.post("/timezone")
async def set_timezone(request: Request):
    data = await request.json()
    init_data = data.get("initData")
    timezone = data.get("timezone")

    if not init_data or timezone not in VALID_TIMEZONES:
        return {"ok": False}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET timezone = $1
            WHERE user_id = $2
        """, timezone, user_id)

    return {"ok": True, "timezone": timezone}


# =====================================================
# 🔹 TOGGLE MEDIA
# =====================================================
@router.post("/toggle_media")
async def toggle_media(request: Request):
    data = await request.json()
    init_data = data.get("initData")

    if not init_data:
        return {"ok": False}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()
    async with pool.acquire() as conn:

        await conn.execute("""
            UPDATE users
            SET share_confirmation_media = NOT share_confirmation_media
            WHERE user_id = $1
        """, user_id)

        row = await conn.fetchrow("""
            SELECT share_confirmation_media
            FROM users
            WHERE user_id = $1
        """, user_id)

    return {
        "ok": True,
        "share_on": row["share_confirmation_media"]
    }