from fastapi import APIRouter, Request
from core.database import get_pool

router = APIRouter()

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
@router.post("/settings")
async def get_settings(request: Request):
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        return {"ok": False, "error": "no user_id"}

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT notification_tone, timezone, share_confirmation_media
            FROM users
            WHERE user_id = $1
        """, user_id)

    if not row:
        return {"ok": False}

    return {
        "ok": True,
        "tone": row["notification_tone"],
        "timezone": row["timezone"],
        "share_on": row["share_confirmation_media"]
    }


# =====================================================
# 🔹 СМЕНА ТОНА
# =====================================================
@router.post("/settings/tone")
async def set_tone(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    tone = data.get("tone")

    if not user_id or tone not in VALID_TONES:
        return {"ok": False}

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET notification_tone = $1
            WHERE user_id = $2
        """, tone, user_id)

    return {"ok": True}


# =====================================================
# 🔹 СМЕНА TIMEZONE
# =====================================================
@router.post("/settings/timezone")
async def set_timezone(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    timezone = data.get("timezone")

    if not user_id or timezone not in VALID_TIMEZONES:
        return {"ok": False}

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET timezone = $1
            WHERE user_id = $2
        """, timezone, user_id)

    return {"ok": True}


# =====================================================
# 🔹 TOGGLE MEDIA
# =====================================================
@router.post("/settings/toggle_media")
async def toggle_media(request: Request):
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        return {"ok": False}

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET share_confirmation_media = NOT share_confirmation_media
            WHERE user_id = $1
        """, user_id)

    return {"ok": True}