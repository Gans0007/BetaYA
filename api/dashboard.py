from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES

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

        # USER STATS + NICKNAME
        row = await conn.fetchrow("""
        SELECT
        COALESCE(s.current_streak,0) as current_streak,
        COALESCE(s.xp,0) as xp,
        COALESCE(s.league,'Безответственный') as league,
        COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname
        FROM user_stats s
        JOIN users u ON u.user_id = s.user_id
        WHERE s.user_id=$1
        """, user_id)


        # =========================
        # ПОЛУЧАЕМ ПРИВЫЧКИ
        # =========================

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

    # =========================
    # ГРУППИРУЕМ ДАННЫЕ
    # =========================

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

        value = 0
        series = []

        today = datetime.utcnow().date()

        for i in range(4, -1, -1):

            day = (today - timedelta(days=i))

            if day == today:

                if day in days:
                    series.append(value + 1)
                else:
                    series.append(value)

            else:

                if day in days:
                    value += 1
                else:
                    value -= 1

                series.append(value)

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

    # =========================
    # XP PROGRESS
    # =========================

    xp_user = float(row["xp"]) if row else 0
    current_league = row["league"] if row else "Безответственный"

    idx = next((i for i,l in enumerate(LEAGUES) if l["name"] == current_league), 0)

    current_xp_need = LEAGUES[idx]["xp"]

    if idx < len(LEAGUES) - 1:
        next_xp_need = LEAGUES[idx + 1]["xp"]
    else:
        next_xp_need = current_xp_need

    xp_progress = xp_user - current_xp_need
    xp_range = next_xp_need - current_xp_need

    xp_percent = int((xp_progress / xp_range) * 100) if xp_range else 100
    xp_percent = max(0, min(100, xp_percent))

    # =========================
    # RETURN
    # =========================

    return {

        "nickname": row["nickname"] if row else "Player",

        "streak": row["current_streak"] if row else 0,

        "xp": xp_user,
        "league": current_league,

        "xp_current": int(xp_user),
        "xp_next": int(next_xp_need),
        "xp_percent": xp_percent,

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
        "me": {
            "rank": my["last_global_rank"] if my else None,
            "username": my["username"] if my else "You",
            "xp": int(my["xp"]) if my else 0
        }
    }