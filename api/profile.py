from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name

router = APIRouter()


@router.post("/api/profile")
async def get_profile(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")
    range_type = data.get("range", "month")

    if range_type not in ("week", "month", "year"):
        range_type = "month"

    if not init_data:
        return {}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        # =========================
        # USER
        # =========================

        user_row = await conn.fetchrow("""
        SELECT
            COALESCE(s.current_streak,0) as current_streak,
            COALESCE(s.xp,0) as xp,
            COALESCE(s.league,'Бронза I') as league,
            COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname
        FROM user_stats s
        JOIN users u ON u.user_id = s.user_id
        WHERE s.user_id=$1
        """, user_id)

        # =========================
        # HABITS
        # =========================

        habits_rows = await conn.fetch("""
        SELECT id
        FROM habits
        WHERE user_id=$1
        AND is_active=true
        """, user_id)

        habit_ids = [h["id"] for h in habits_rows]

        confirmations_rows = await conn.fetch("""
        SELECT habit_id, DATE(datetime) as day
        FROM confirmations
        WHERE user_id=$1
        AND datetime >= NOW() - INTERVAL '365 days'
        """, user_id)

    # =========================
    # ДАТЫ ДЛЯ RANGE
    # =========================

    today = datetime.now().date()

    if range_type == "week":
        start_date = today - timedelta(days=6)
    elif range_type == "year":
        start_date = datetime(today.year, 1, 1).date()
    else:
        start_date = datetime(today.year, today.month, 1).date()

    # =========================
    # ГРУППИРУЕМ CONFIRMATIONS
    # =========================

    confirmations = {}

    for r in confirmations_rows:
        hid = r["habit_id"]
        day = r["day"]

        if hid not in confirmations:
            confirmations[hid] = set()

        confirmations[hid].add(day)

    # =========================
    # BEHAVIOR
    # =========================

    completed = 0
    missed = 0

    d = start_date

    while d <= today:

        done_count = 0

        for hid in habit_ids:
            if hid in confirmations and d in confirmations[hid]:
                done_count += 1

        completed += done_count
        missed += (len(habit_ids) - done_count)

        d += timedelta(days=1)

    index = 0
    total = completed + missed

    if total > 0:
        index = int((completed / total) * 100)

    # =========================
    # HEATMAP
    # =========================

    heatmap = []

    d = start_date

    while d <= today:

        value = 0

        for hid in habit_ids:
            if hid in confirmations and d in confirmations[hid]:
                value += 1

        heatmap.append({
            "date": d.isoformat(),
            "value": value
        })

        d += timedelta(days=1)

    # =========================
    # GRAPH (behavior curve)
    # =========================

    graph = []

    score = 0

    d = start_date

    while d <= today:

        done_count = 0

        for hid in habit_ids:
            if hid in confirmations and d in confirmations[hid]:
                done_count += 1
 
        total_today = len(habit_ids)
  
        # баланс дня
        day_score = done_count - (total_today - done_count)

        score += day_score

        graph.append({
            "date": d.isoformat(),
            "score": score
        })

        d += timedelta(days=1)

    # =========================
    # USER DATA (XP / LEAGUE)
    # =========================

    xp_user = float(user_row["xp"]) if user_row else 0
    current_league = user_row["league"] if user_row else "Бронза I"

    idx = next((i for i, l in enumerate(LEAGUES) if l["name"] == current_league), 0)

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

    # =========================
    # RESPONSE
    # =========================

    return {

        "user": {
            "nickname": user_row["nickname"] if user_row else "Player",
            "league": {
                "name": league_obj["name"],
                "icon": f"/img/leagues/{league_obj['icon']}"
            },
            "xp_current": int(xp_user),
            "xp_next": int(next_xp_need),
            "xp_percent": xp_percent
        },

        "behavior": {
            "completed": completed,
            "missed": missed,
            "index": index
        },

        "heatmap": heatmap,
        "graph": graph
    }