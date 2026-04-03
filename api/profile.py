from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name

router = APIRouter()

AVAILABLE_AVATARS = {
    "avatar_1.png",
    "avatar_2.png",
    "avatar_3.png",
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

    today = datetime.now().date()

    # =========================
    # WEEK (ПН–ВС)
    # =========================
    if range_type == "week":
        start_date = today - timedelta(days=today.weekday())  # ПН
        end_date = start_date + timedelta(days=6)             # ВС

    # =========================
    # MONTH (1–последний день)
    # =========================
    elif range_type == "month":
        start_date = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)

        end_date = next_month - timedelta(days=1)

    # =========================
    # YEAR (1 янв – 31 дек)
    # =========================
    elif range_type == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

    else:
        start_date = today - timedelta(days=6)
        end_date = today

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
    SELECT DATE(datetime) as day, COUNT(DISTINCT habit_id) as done_count
    FROM confirmations
    WHERE user_id = $1
    AND datetime >= $2
    AND datetime <= $3
    GROUP BY DATE(datetime)
    """, user_id, start_date, end_date)

        # 🔥 супер быстрый словарь
        day_counts = {r["day"]: r["done_count"] for r in confirmations_rows}
 
        total_habits = len(habit_ids)

        completed = 0
        missed = 0
        heatmap = []
        graph = []

        score = 0
        d = start_date

        real_end_date = min(end_date, today)

        while d <= end_date:
            done = day_counts.get(d, 0)

            # =========================
            # ТОЛЬКО ПРОШЛОЕ → В АНАЛИТИКУ
            # =========================
            if d <= real_end_date:
                completed += done
                missed += (total_habits - done)

            # =========================
            # ВСЁ → В ОТОБРАЖЕНИЕ
            # =========================
            heatmap.append({
                "date": d.isoformat(),
                "value": done
            })

            if total_habits > 0:
                day_score = done - (total_habits - done)
            else:
                day_score = 0

            if d <= real_end_date:
                score += day_score

            graph.append({
                "date": d.isoformat(),
                "score": score
            })

            d += timedelta(days=1)

    index = 0
    total = completed + missed

    if total > 0:
        index = int((completed / total) * 100)

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

    xp_percent = int((xp_progress / xp_range) * 100) if xp_range > 0 else 100
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
        "graph": graph,

        "period_label": period_label,
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

    today = datetime.now().date()

    if range_type == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    elif range_type == "month":
        start_date = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)

        end_date = next_month - timedelta(days=1)

    elif range_type == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

    else:
        start_date = today - timedelta(days=6)
        end_date = today 

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
        SELECT DATE(datetime) as day, COUNT(DISTINCT habit_id) as done_count
        FROM confirmations
        WHERE user_id = $1
        AND datetime >= $2
        AND datetime <= $3
        GROUP BY DATE(datetime)
        """, target_user_id, start_date, end_date)

        day_counts = {r["day"]: r["done_count"] for r in confirmations_rows}
 
        total_habits = len(habit_ids)

        completed = 0
        missed = 0
        heatmap = []
        graph = []

        score = 0
        d = start_date

        real_end_date = min(end_date, today)
  
        while d <= end_date:
            done = day_counts.get(d, 0)

            if d <= real_end_date:
                completed += done
                missed += (total_habits - done)

            heatmap.append({
                "date": d.isoformat(),
                "value": done
            })

            if total_habits > 0:
                day_score = done - (total_habits - done)
            else:
                day_score = 0
   
            if d <= real_end_date:
                score += day_score

            graph.append({
                "date": d.isoformat(),
                "score": score
            })

            d += timedelta(days=1)

    index = 0
    total = completed + missed

    if total > 0:
        index = int((completed / total) * 100)

    xp_user = float(user_row["xp"] or 0)
    current_league = user_row["league"]

    idx = next((i for i, l in enumerate(LEAGUES) if l["name"] == current_league), 0)

    current_xp_need = LEAGUES[idx]["xp"]

    if idx < len(LEAGUES) - 1:
        next_xp_need = LEAGUES[idx + 1]["xp"]
    else:
        next_xp_need = current_xp_need

    xp_progress = xp_user - current_xp_need
    xp_range = next_xp_need - current_xp_need

    xp_percent = int((xp_progress / xp_range) * 100) if xp_range > 0 else 100
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