from datetime import datetime, timedelta
from fastapi import APIRouter, Request
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
        return {"habits": []}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        # USER STATS
        row = await conn.fetchrow("""
        SELECT
        COALESCE(current_streak,0) as current_streak,
        COALESCE(xp,0) as xp,
        COALESCE(league,'Безответственный') as league
        FROM user_stats
        WHERE user_id=$1
        """, user_id)


        # ОДИН SQL НА ВСЕ ПРИВЫЧКИ
        rows = await conn.fetch("""

        SELECT
            h.id,
            h.name,
            DATE(c.datetime) as day

        FROM habits h

        LEFT JOIN confirmations c
            ON c.habit_id = h.id
            AND c.user_id = h.user_id
            AND c.datetime >= NOW() - INTERVAL '30 days'

        WHERE h.user_id = $1
        AND h.is_active = true

        ORDER BY h.id, day

        """, user_id)

    # =========================================
    # ГРУППИРУЕМ ДАННЫЕ
    # =========================================

    habits_map = {}

    for r in rows:

        hid = r["id"]

        if hid not in habits_map:

            habits_map[hid] = {
                "id": hid,
                "name": r["name"],
                "days": set()
            }

        if r["day"]:
            habits_map[hid]["days"].add(r["day"])


    habits = []

    for habit in habits_map.values():

        days = habit["days"]

        # SERIES (+1 / -1)
        value = 0
        series = []

        today = datetime.utcnow().date()

        for i in range(4, -1, -1):

            day = (today - timedelta(days=i))

            # если это сегодняшний день
            if day == today:

                if day in days:
                    series.append(value + 1)
                else:
                    # сегодня еще не подтверждено → точка 0
                    series.append(value)

            else:

                if day in days:
                    value += 1
                else:
                    value -= 1

                series.append(value)

        # ACTIVE STREAK

        streak = 0

        for i in range(365):

            day = (datetime.utcnow() - timedelta(days=i)).date()

            if day in days:
                streak += 1
            else:
                break

        habits.append({

            "id": habit["id"],
            "name": habit["name"],
            "series": series,
            "streak": streak,
            "days": [d.isoformat() for d in days]

        })

    return {

        "streak": row["current_streak"] if row else 0,
        "xp": float(row["xp"]) if row else 0,
        "league": row["league"] if row else "Безответственный",

        "habits": habits

    }

# =========================
# LEADERBOARD
# =========================

@router.post("/api/leaderboard")
async def get_leaderboard(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {"leaders": []}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        # TOP 10
        rows = await conn.fetch("""

        SELECT
            u.last_global_rank,
            COALESCE(u.username, u.first_name, 'Unknown') as username,
            s.xp

        FROM users u
        JOIN user_stats s ON s.user_id = u.user_id

        WHERE u.last_global_rank IS NOT NULL

        ORDER BY u.last_global_rank
        LIMIT 10

        """)

        # МОЕ МЕСТО
        my = await conn.fetchrow("""

        SELECT
            u.last_global_rank,
            COALESCE(u.username, u.first_name, 'You') as username,
            s.xp

        FROM users u
        JOIN user_stats s ON s.user_id = u.user_id

        WHERE u.user_id=$1

        """, user_id)

    leaders = []

    for r in rows:

        leaders.append({
            "rank": r["last_global_rank"],
            "username": r["username"],
            "xp": int(r["xp"])
        })

    return {

        "leaders": leaders,

        "my_rank": my["last_global_rank"] if my else None,
        "my_xp": int(my["xp"]) if my else 0,
        "my_username": my["username"] if my else None

    }