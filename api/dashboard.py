from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name

router = APIRouter()


# =========================
# USER
# =========================

@router.post("/api/user")
async def get_user(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow("""
        SELECT
            COALESCE(s.current_streak,0) as current_streak,
            COALESCE(s.xp,0) as xp,
            COALESCE(s.league,'Бронза I') as league,
            COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname
        FROM user_stats s
        JOIN users u ON u.user_id = s.user_id
        WHERE s.user_id=$1
        """, user_id)

    xp_user = float(row["xp"]) if row else 0
    current_league = row["league"] if row else "Бронза I"

    idx = next((i for i,l in enumerate(LEAGUES) if l["name"] == current_league), 0)

    current_xp_need = LEAGUES[idx]["xp"]

    if idx < len(LEAGUES) - 1:
        next_xp_need = LEAGUES[idx + 1]["xp"]
    else:
        next_xp_need = current_xp_need

    xp_progress = xp_user - current_xp_need
    xp_range = next_xp_need - current_xp_need


    if xp_range > 0:
        xp_percent = int((xp_progress / xp_range) * 100)
    else:
        xp_percent = 100

    xp_percent = max(0, min(100, xp_percent))

    league_obj = get_league_by_name(current_league) or LEAGUES[0]

    return {

        "nickname": row["nickname"] if row else "Player",
        "streak": row["current_streak"] if row else 0,

        "xp": xp_user,
        "league": {
           "name": league_obj["name"],
            "icon": f"/img/leagues/{league_obj['icon']}"
        },
        "xp_current": int(xp_user),
        "xp_next": int(next_xp_need),
        "xp_percent": xp_percent

    }


# =========================
# HABITS
# =========================

@router.post("/api/habits")
async def get_habits(request: Request):

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

        habits_rows = await conn.fetch("""
        SELECT id, name
        FROM habits
        WHERE user_id=$1
        AND is_active=true
        ORDER BY id
        """, user_id)

        confirmations_rows = await conn.fetch("""
        SELECT habit_id, DATE(datetime) as day
        FROM confirmations
        WHERE user_id=$1
        AND datetime >= NOW() - INTERVAL '365 days'
        """, user_id)

    # =========================
    # ГРУППИРУЕМ CONFIRMATIONS
    # =========================

    confirmations = {}

    for r in confirmations_rows:

        hid = r["habit_id"]

        if hid not in confirmations:
            confirmations[hid] = set()

        confirmations[hid].add(r["day"])

    habits = []

    today = datetime.now().date()

    for h in habits_rows:

        hid = h["id"]
        name = h["name"]

        days = confirmations.get(hid, set())

        # =========================
        # STREAK (подряд дни)
        # =========================

        streak = 0
        check_day = today

        while check_day in days:
            streak += 1
            check_day -= timedelta(days=1)

        # =========================
        # SERIES ДЛЯ ГРАФИКА
        # =========================

        value = 0
        series = []

        for i in range(4, -1, -1):

            day = today - timedelta(days=i)

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

        habits.append({

            "id": hid,
            "name": name,
            "series": series,
            "streak": streak,
            "days": [d.isoformat() for d in days]

        })

    return {"habits": habits}


# =========================
# REFERRALS
# =========================

@router.post("/api/referrals")
async def get_referrals(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {"referrals": []}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        ref_rows = await conn.fetch("""

        SELECT
            u.user_id,
            COALESCE(u.username, u.first_name, 'User') as name,
            COALESCE(s.xp,0) as xp

        FROM referrals r
        JOIN users u ON u.user_id = r.user_id
        LEFT JOIN user_stats s ON s.user_id = u.user_id

        WHERE r.affiliate_id=$1

        ORDER BY s.xp DESC

        """, user_id)

    referrals = []

    for r in ref_rows:

        referrals.append({
            "user_id": r["user_id"],
            "name": r["name"],
            "xp": int(r["xp"])
        })

    return {"referrals": referrals}


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
        LIMIT 100

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
