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

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {
            "streak": 0,
            "xp": 0,
            "league": "Безответственный"
        }

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow("""
            SELECT
                COALESCE(current_streak,0) as streak,
                COALESCE(xp,0) as xp,
                COALESCE(league,'Безответственный') as league
            FROM user_stats
            WHERE user_id=$1
        """, user_id)

    if not row:
        return {"streak":0,"xp":0,"league":"Безответственный"}

    return dict(row)


# =========================================
# HABITS
# =========================================

@router.post("/api/habits")
async def get_habits(request: Request):

    data = await request.json()

    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(400,"initData missing")

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
            SELECT
                id,
                name,
                done_days,
                days
            FROM habits
            WHERE user_id=$1
            AND is_active=true
            ORDER BY created_at
        """, user_id)

    return {
        "habits":[dict(r) for r in rows]
    }



@router.post("/api/habit_history")
async def get_habit_history(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
        SELECT
            h.id as habit_id,
            h.name as habit_name,
            DATE(c.datetime) as day,
            c.confirmed
        FROM confirmations c
        JOIN habits h ON h.id = c.habit_id
        WHERE c.user_id = $1
        ORDER BY day
        """, user_id)

    return {
        "history": [dict(r) for r in rows]
    }