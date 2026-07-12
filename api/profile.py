from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name
from data.achievements_data import ALL_ACHIEVEMENTS

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

    async with pool.acquire() as conn:
        user_timezone = await conn.fetchval("""
            SELECT COALESCE(timezone, 'Europe/Kyiv')
            FROM users
            WHERE user_id = $1
        """, user_id)

    user_timezone = user_timezone or "Europe/Kyiv"

    try:
        user_tz = ZoneInfo(user_timezone)
    except Exception:
        user_timezone = "Europe/Kyiv"
        user_tz = ZoneInfo(user_timezone)

    now_local = datetime.now(user_tz)
    today = now_local.date()

    if range_type == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    elif range_type == "month":
        start_date = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1
            )
        else:
            next_month = today.replace(
                month=today.month + 1,
                day=1
            )

        end_date = next_month - timedelta(days=1)
 
    elif range_type == "year":
        start_date = today.replace(
            month=1,
            day=1
        )

        end_date = today.replace(
            month=12,
            day=31
        )

    else:
        start_date = today
        end_date = today

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=user_tz
    )

    end_datetime_exclusive = datetime.combine(
        end_date + timedelta(days=1),
        datetime.min.time(),
        tzinfo=user_tz
    )  

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

        habits = await conn.fetch("""
        SELECT id, created_at, completed_at
        FROM habits
        WHERE user_id = $1
        """, user_id)

        confirmations_rows = await conn.fetch("""
            SELECT
                DATE(datetime AT TIME ZONE $4) AS day,
                COUNT(DISTINCT habit_id) AS done_count
            FROM confirmations
            WHERE user_id = $1
              AND datetime >= $2
              AND datetime < $3
              AND (confirmed = TRUE OR confirmed IS NULL)
            GROUP BY DATE(datetime AT TIME ZONE $4)
        """,
            user_id,
            start_datetime,
            end_datetime_exclusive,
            user_timezone
        )

        day_counts = {r["day"]: r["done_count"] for r in confirmations_rows}

        completed = 0
        missed = 0
        heatmap = []
        graph = []

        score = 0
        d = start_date
        real_end_date = min(end_date, today)

        def habit_exists_on_day(habit, day):
            start = habit["created_at"].date()
            end = habit["completed_at"].date() if habit["completed_at"] else today
            return start <= day <= end

        while d <= end_date:
            done = day_counts.get(d, 0)

            active_today = sum(
                1 for h in habits if habit_exists_on_day(h, d)
            )

            if d <= real_end_date:
                completed += done
                missed += max(0, active_today - done)

            heatmap.append({
                "date": d.isoformat(),
                "value": done
            })

            if active_today > 0:
                day_score = done - max(0, active_today - done)
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

    if range_type == "week":
        period_label = f"{start_date.strftime('%d.%m')} – {end_date.strftime('%d.%m')}"

    elif range_type == "month":
        RU_MONTHS = {
            1: "Январь",
            2: "Февраль",
            3: "Март",
            4: "Апрель",
            5: "Май",
            6: "Июнь",
            7: "Июль",
            8: "Август",
            9: "Сентябрь",
            10: "Октябрь",
            11: "Ноябрь",
            12: "Декабрь",
        }

        period_label = RU_MONTHS[start_date.month]

    elif range_type == "year":
        period_label = start_date.strftime("%Y")

    else:
        period_label = ""

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

    async with pool.acquire() as conn:
        user_timezone = await conn.fetchval("""
            SELECT COALESCE(timezone, 'Europe/Kyiv')
            FROM users
            WHERE user_id = $1
        """, target_user_id)

    user_timezone = user_timezone or "Europe/Kyiv"

    try:
        user_tz = ZoneInfo(user_timezone)
    except Exception:
        user_timezone = "Europe/Kyiv"
        user_tz = ZoneInfo(user_timezone)

    now_local = datetime.now(user_tz)
    today = now_local.date()

    if range_type == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    elif range_type == "month":
        start_date = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1
            )
        else:
            next_month = today.replace(
                month=today.month + 1,
                day=1
            )

        end_date = next_month - timedelta(days=1)

    elif range_type == "year":
        start_date = today.replace(
            month=1,
            day=1
        )

        end_date = today.replace(
            month=12,
            day=31
        )

    else:
        start_date = today
        end_date = today

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=user_tz
    )

    end_datetime_exclusive = datetime.combine(
        end_date + timedelta(days=1),
        datetime.min.time(),
        tzinfo=user_tz
    )

    async with pool.acquire() as conn:

        user_row = await conn.fetchrow("""
        SELECT
            u.joined_at,
            COALESCE(u.has_access, false) AS has_access,

            COALESCE(s.current_streak, 0) AS current_streak,
            COALESCE(s.max_streak, 0) AS max_streak,
            COALESCE(s.xp, 0)::float AS xp,
            COALESCE(s.finished_habits, 0) AS finished_habits,
            COALESCE(s.finished_challenges, 0) AS finished_challenges,
            COALESCE(s.total_confirmed_days, 0) AS total_confirmed_days,
            COALESCE(s.league, 'Бронза I') AS league,

            COALESCE(
                u.nickname,
                u.username,
                u.first_name,
                'Player'
            ) AS nickname,

            COALESCE(
                u.avatar,
                'avatar_1.png'
            ) AS avatar

        FROM users u

        LEFT JOIN user_stats s
            ON u.user_id = s.user_id

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
                "data": {
                    "joined_at": "—",
                    "has_access": False,
                    "finished_habits": 0,
                    "finished_challenges": 0,
                    "xp": 0,
                    "total_confirmed_days": 0,
                    "current_streak": 0,
                    "max_streak": 0,
                    "league": "Бронза I",
                    "achievements": [],
                    "achievements_received": 0,
                    "achievements_total": 0
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

        habits = await conn.fetch("""
        SELECT
            id,
            created_at,
            completed_at
        FROM habits
        WHERE user_id = $1
        """, target_user_id)

        confirmations_rows = await conn.fetch("""
        SELECT
            DATE(datetime AT TIME ZONE $4) AS day,
            COUNT(DISTINCT habit_id) AS done_count
        FROM confirmations
        WHERE user_id = $1
          AND datetime >= $2
          AND datetime < $3
          AND (confirmed = TRUE OR confirmed IS NULL)
        GROUP BY DATE(datetime AT TIME ZONE $4)
    """,
        target_user_id,
        start_datetime,
        end_datetime_exclusive,
        user_timezone
    )

        day_counts = {
            row["day"]: row["done_count"]
            for row in confirmations_rows
        }

        completed = 0
        missed = 0
        heatmap = []
        graph = []

        score = 0
        d = start_date
        real_end_date = min(end_date, today)

        def habit_exists_on_day(habit, day):
            start = habit["created_at"].date()

            end = (
                habit["completed_at"].date()
                if habit["completed_at"]
                else today
            )

            return start <= day <= end

        while d <= end_date:

            done = day_counts.get(d, 0)

            active_today = sum(
                1
                for habit in habits
                if habit_exists_on_day(habit, d)
            )

            if d <= real_end_date:
                completed += done
                missed += max(0, active_today - done)

            heatmap.append({
                "date": d.isoformat(),
                "value": done
            })

            if active_today > 0:
                day_score = (
                    done -
                    max(0, active_today - done)
                )
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
        index = int(
            (completed / total) * 100
        )

    xp_user = float(user_row["xp"] or 0)
    current_league = (
        user_row["league"]
        or "Бронза I"
    )

    idx = next(
        (
            i
            for i, league in enumerate(LEAGUES)
            if league["name"] == current_league
        ),
        0
    )

    current_xp_need = LEAGUES[idx]["xp"]

    if idx < len(LEAGUES) - 1:
        next_xp_need = LEAGUES[idx + 1]["xp"]
    else:
        next_xp_need = current_xp_need

    xp_progress = xp_user - current_xp_need
    xp_range = next_xp_need - current_xp_need

    xp_percent = (
        int((xp_progress / xp_range) * 100)
        if xp_range > 0
        else 100
    )

    xp_percent = max(
        0,
        min(100, xp_percent)
    )

    league_obj = (
        get_league_by_name(current_league)
        or LEAGUES[0]
    )

    joined_at = user_row["joined_at"]

    if joined_at:
        joined_at = joined_at.strftime("%d.%m.%Y")
    else:
        joined_at = "—"

    current_streak = (
        user_row["current_streak"]
        or 0
    )

    all_achievements = []

    for category_items in ALL_ACHIEVEMENTS.values():

        for achievement in category_items:

            unlocked = False

            if achievement["condition_type"] == "streak":
                unlocked = (
                    current_streak
                    >= achievement["condition_value"]
                )

            all_achievements.append({
                "code": achievement["code"],
                "category": achievement["category"],
                "title": achievement["title"],
                "description": achievement["description"],
                "icon": achievement.get("icon"),
                "image": achievement.get("image"),
                "condition_type": achievement["condition_type"],
                "condition_value": achievement["condition_value"],
                "xp_reward": achievement.get(
                    "xp_reward",
                    0
                ),
                "usdt_reward": achievement.get(
                    "usdt_reward",
                    0
                ),
                "unlocked": unlocked
            })

    achievements_received = sum(
        1
        for achievement in all_achievements
        if achievement["unlocked"]
    )

    achievements_total = len(
        all_achievements
    )

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

        "data": {
            "joined_at": joined_at,
            "has_access": bool(
                user_row["has_access"]
            ),

            "finished_habits": user_row[
                "finished_habits"
            ],

            "finished_challenges": user_row[
                "finished_challenges"
            ],

            "xp": int(xp_user),

            "total_confirmed_days": user_row[
                "total_confirmed_days"
            ],

            "current_streak": user_row[
                "current_streak"
            ],

            "max_streak": user_row[
                "max_streak"
            ],

            "league": current_league,

            "achievements": all_achievements,

            "achievements_received":
                achievements_received,

            "achievements_total":
                achievements_total
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

@router.post("/api/profile/data")
async def get_profile_data(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {"status": "error", "message": "missing_init_data"}

    user_id = validate_telegram_data(init_data)
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT
            u.joined_at,
            COALESCE(u.has_access, false) AS has_access,

            COALESCE(s.finished_habits, 0) AS finished_habits,
            COALESCE(s.finished_challenges, 0) AS finished_challenges,
            COALESCE(s.xp, 0)::int AS xp,
            COALESCE(s.total_confirmed_days, 0) AS total_confirmed_days,
            COALESCE(s.current_streak, 0) AS current_streak,
            COALESCE(s.max_streak, 0) AS max_streak,
            COALESCE(s.league, 'Бронза I') AS league

        FROM users u
        LEFT JOIN user_stats s ON u.user_id = s.user_id
        WHERE u.user_id = $1
        """, user_id)

    if not row:
        return {"status": "error", "message": "user_not_found"}

    joined_at = row["joined_at"]

    if joined_at:
        joined_at = joined_at.strftime("%d.%m.%Y")
    else:
        joined_at = "—"

    current_streak = row["current_streak"] or 0

    all_achievements = []

    for category_items in ALL_ACHIEVEMENTS.values():
        for achievement in category_items:

            unlocked = False

            if achievement["condition_type"] == "streak":
                unlocked = current_streak >= achievement["condition_value"]

            all_achievements.append({
                "code": achievement["code"],
                "category": achievement["category"],
                "title": achievement["title"],
                "description": achievement["description"],
                "icon": achievement.get("icon"),
                "image": achievement.get("image"),
                "condition_type": achievement["condition_type"],
                "condition_value": achievement["condition_value"],
                "xp_reward": achievement.get("xp_reward", 0),
                "usdt_reward": achievement.get("usdt_reward", 0),
                "unlocked": unlocked
            })

    achievements_received = sum(
        1 for achievement in all_achievements
        if achievement["unlocked"]
    )

    achievements_total = len(all_achievements)

    return {
        "status": "ok",
        "data": {
            "joined_at": joined_at,
            "has_access": bool(row["has_access"]),

            "finished_habits": row["finished_habits"],
            "finished_challenges": row["finished_challenges"],
            "xp": row["xp"],
            "total_confirmed_days": row["total_confirmed_days"],
            "current_streak": row["current_streak"],
            "max_streak": row["max_streak"],
            "league": row["league"],

            "achievements": all_achievements,
            "achievements_received": achievements_received,
            "achievements_total": achievements_total
        }
    }