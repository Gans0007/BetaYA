from fastapi import APIRouter, Request, HTTPException
from api.telegram_auth import validate_telegram_data
from core.database import get_pool

router = APIRouter()


# =========================================
# DASHBOARD
# streak / xp / league
# =========================================

@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    # безопасно читаем JSON
    try:
        data = await request.json()
    except Exception:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {
            "telegram_user_id": None,
            "streak": 0,
            "xp": 0,
            "league": "Безответственный",
            "debug": "initData missing"
        }

    # проверяем подпись Telegram
    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT
                COALESCE(current_streak, 0) as current_streak,
                COALESCE(xp, 0) as xp,
                COALESCE(league, 'Безответственный') as league
            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

    return {
        "telegram_user_id": user_id,
        "streak": row["current_streak"] if row else 0,
        "xp": float(row["xp"]) if row else 0,
        "league": row["league"] if row else "Безответственный"
    }


# =========================================
# HABITS
# список привычек пользователя
# =========================================

@router.post("/api/habits")
async def get_habits(request: Request):

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    # проверяем Telegram
    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        habits = await conn.fetch(
            """
            SELECT
                id,
                name,
                done_days,
                days
            FROM habits
            WHERE user_id = $1
            AND is_active = TRUE
            ORDER BY created_at
            """,
            user_id
        )

    return {
        "habits": [dict(h) for h in habits]
    }