from fastapi import APIRouter, Request, HTTPException
from api.telegram_auth import validate_telegram_data
from core.database import get_pool

router = APIRouter()


@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    try:
        data = await request.json()
    except:
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


@router.post("/api/habits")
async def get_habits(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
        SELECT id, name, done_days
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
            h.name,
            DATE(h.created_at) as created_day,
            DATE(c.datetime) as confirm_day
        FROM habits h
        LEFT JOIN confirmations c
            ON h.id = c.habit_id
            AND c.confirmed = true
        WHERE h.user_id=$1
        AND h.is_active=true
        ORDER BY h.id, confirm_day
        """, user_id)

    return {
        "history":[dict(r) for r in rows]
    }



@router.post("/api/month_confirmations")
async def month_confirmations(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""

        SELECT
            TO_CHAR(m.month,'YYYY-MM') as month,
            COALESCE(COUNT(c.id),0) as total

        FROM generate_series(
            date_trunc('month', NOW()) - interval '11 months',
            date_trunc('month', NOW()),
            interval '1 month'
        ) m(month)

        LEFT JOIN confirmations c
            ON date_trunc('month', c.datetime) = m.month
            AND c.user_id = $1
            AND c.confirmed = true

        GROUP BY m.month
        ORDER BY m.month

        """, user_id)

    return {
        "months":[dict(r) for r in rows]
    }