from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name

router = APIRouter()

AVAILABLE_AVATARS = {
    "avatar_1.png",
    "avatar_2.png"
}


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

        user_row = await conn.fetchrow("""
        SELECT
            COALESCE(s.current_streak, 0) as current_streak,
            COALESCE(s.xp, 0)::float as xp,
            COALESCE(s.league, 'Бронза I') as league,
            COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname,
            COALESCE(u.avatar, 'avatar_1.png') as avatar
        FROM users u
        LEFT JOIN user_stats s ON u.user_id = s.user_id
        WHERE u.user_id = $1
        """, user_id)

        habits_rows = await conn.fetch("""
        SELECT id
        FROM habits
        WHERE user_id = $1
        AND is_active = true
        """, user_id)

        habit_ids = [h["id"] for h in habits_rows]

        confirmations_rows = await conn.fetch("""
        SELECT habit_id, DATE(datetime) as day
        FROM confirmations
        WHERE user_id = $1
        AND datetime >= NOW() - INTERVAL '365 days'
        """, user_id)

    today = datetime.now().date()

    if range_type == "week":
        start_date = today - timedelta(days=6)
    elif range_type == "year":
        start_date = datetime(today.year, 1, 1).date()
    else:
        start_date = datetime(today.year, today.month, 1).date()

    confirmations = {}

    for r in confirmations_rows:
        hid = r["habit_id"]
        day = r["day"]

        if hid not in confirmations:
            confirmations[hid] = set()

        confirmations[hid].add(day)

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

    graph = []
    score = 0
    d = start_date

    while d <= today:

        done_count = 0

        for hid in habit_ids:
            if hid in confirmations and d in confirmations[hid]:
                done_count += 1

        total_today = len(habit_ids)
        day_score = done_count - (total_today - done_count)
        score += day_score

        graph.append({
            "date": d.isoformat(),
            "score": score
        })

        d += timedelta(days=1)

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

    return {
        "user": {
            "nickname": user_row["nickname"] if user_row else "Player",
            "avatar": user_row["avatar"] if user_row else "avatar_1.png",
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


@router.post("/api/profile/avatar")
async def update_avatar(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")
    avatar = data.get("avatar")

    if not init_data or not avatar:
        return {"status": "error", "message": "missing_data"}

    if avatar not in AVAILABLE_AVATARS:
        return {"status": "error", "message": "invalid_avatar"}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE users
        SET avatar = $1
        WHERE user_id = $2
        """, avatar, user_id)

    return {
        "status": "ok",
        "avatar": avatar
    }



@router.post("/api/profile/view")
async def view_profile(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    try:
        target_user_id = int(data.get("user_id"))
    except:
        return {"status": "error", "message": "invalid_user_id"}

    range_type = data.get("range", "month")

    if range_type not in ("week", "month", "year"):
        range_type = "month"

    if not target_user_id:
        return {"status": "error", "message": "missing_user_id"}

    pool = await get_pool()

    async with pool.acquire() as conn:

        user_row = await conn.fetchrow("""
        SELECT
            COALESCE(s.current_streak, 0) as current_streak,
            COALESCE(s.xp, 0)::float as xp,
            COALESCE(s.league, 'Бронза I') as league,
            COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname,
            COALESCE(u.avatar, 'avatar_1.png') as avatar
        FROM users u
        LEFT JOIN user_stats s ON u.user_id = s.user_id
        WHERE u.user_id = $1
        """, target_user_id)

        if not user_row:
            return {
                "user": {
                    "nickname": "Player",
                    "avatar": "avatar_1.png",
                    "league": {
                        "name": "Бронза I",
                        "icon": "/img/leagues/bronze_1.png"
                    },
                    "xp_current": 0,
                    "xp_next": 100,
                    "xp_percent": 0
                },
                "behavior": {
                    "completed": 0,
                    "missed": 0,
                    "index": 0
                },
                "heatmap": [],
                "graph": [],
                "is_view_only": True
            }

        habits_rows = await conn.fetch("""
        SELECT id
        FROM habits
        WHERE user_id = $1
        AND is_active = true
        """, target_user_id)

        habit_ids = [h["id"] for h in habits_rows]

        confirmations_rows = await conn.fetch("""
        SELECT habit_id, DATE(datetime) as day
        FROM confirmations
        WHERE user_id = $1
        AND datetime >= NOW() - INTERVAL '365 days'
        """, target_user_id)

    today = datetime.now().date()

    if range_type == "week":
        start_date = today - timedelta(days=6)
    elif range_type == "year":
        start_date = datetime(today.year, 1, 1).date()
    else:
        start_date = datetime(today.year, today.month, 1).date()

    confirmations = {}

    for r in confirmations_rows:
        hid = r["habit_id"]
        day = r["day"]

        if hid not in confirmations:
            confirmations[hid] = set()

        confirmations[hid].add(day)

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

    graph = []
    score = 0
    d = start_date

    while d <= today:

        done_count = 0

        for hid in habit_ids:
            if hid in confirmations and d in confirmations[hid]:
                done_count += 1

        total_today = len(habit_ids)
        day_score = done_count - (total_today - done_count)
        score += day_score

        graph.append({
            "date": d.isoformat(),
            "score": score
        })

        d += timedelta(days=1)

    xp_user = float(user_row["xp"] or 0) if user_row else 0
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

    return {
        "user": {
            "nickname": user_row["nickname"],
            "avatar": user_row["avatar"],
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
        "graph": graph,
        "is_view_only": True
    }