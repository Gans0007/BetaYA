from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool
from services.xp_service import LEAGUES, get_league_by_name
from services.leaderboard.season_service import get_current_season_info

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
            COALESCE(s.current_streak, 0) as current_streak,
            COALESCE(s.xp, 0) as xp,
            COALESCE(s.total_stars, 0) as total_stars,
            COALESCE(s.league, 'Бронза I') as league,
            COALESCE(u.nickname, u.username, u.first_name, 'Player') as nickname,
            COALESCE(u.avatar, 'avatar_1.png') as avatar,
            COALESCE(u.referral_code, '') as referral_code
        FROM user_stats s
        JOIN users u ON u.user_id = s.user_id
        WHERE s.user_id = $1
        """, user_id)

    bot_username = "LiteVAmbitionBot"

    referral_code = row["referral_code"] if row and row["referral_code"] else ""

    ref_link = (
        f"https://t.me/{bot_username}?start={referral_code}"
        if referral_code else ""
    )

    xp_user = float(row["xp"]) if row else 0
    stars_user = int(row["total_stars"]) if row else 0
    current_league = row["league"] if row else "Бронза I"

    idx = next((i for i, l in enumerate(LEAGUES) if l["name"] == current_league), 0)

    current_xp_need = LEAGUES[idx]["xp"]
    current_stars_need = LEAGUES[idx]["stars"]

    if idx < len(LEAGUES) - 1:
        next_league = LEAGUES[idx + 1]

        next_xp_need = next_league["xp"]
        next_stars_need = next_league["stars"]
    else:
        next_xp_need = current_xp_need
        next_stars_need = current_stars_need

    xp_progress = xp_user - current_xp_need
    xp_range = next_xp_need - current_xp_need

    if xp_range > 0:
        xp_percent = int((xp_progress / xp_range) * 100)
    else:
        xp_percent = 100

    xp_percent = max(0, min(100, xp_percent))

    # =========================
    # STARS PROGRESS
    # =========================

    stars_progress = stars_user - current_stars_need
    stars_range = next_stars_need - current_stars_need

    if stars_range > 0:
        stars_percent = int((stars_progress / stars_range) * 100)
    else:
        stars_percent = 100

    stars_percent = max(0, min(100, stars_percent))

    league_obj = get_league_by_name(current_league) or LEAGUES[0]

    return {
        "nickname": row["nickname"] if row else "Player",
        "streak": row["current_streak"] if row else 0,
        "avatar": row["avatar"] if row else "avatar_1.png",
        "xp": xp_user,
        "ref_link": ref_link,
        "league": {
            "name": league_obj["name"],
            "icon": f"/img/leagues/{league_obj['icon']}"
        },
        "xp_current": int(xp_user),
        "xp_next": int(next_xp_need),
        "xp_percent": xp_percent,
        "stars_current": int(stars_user),
        "stars_next": int(next_stars_need),
        "stars_percent": stars_percent,
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

        # 🌍 timezone пользователя
        user_row = await conn.fetchrow("""
        SELECT COALESCE(timezone, 'Europe/Kyiv') as timezone
        FROM users
        WHERE user_id=$1
        """, user_id)

        user_timezone = user_row["timezone"] if user_row else "Europe/Kyiv"

        habits_rows = await conn.fetch("""
        SELECT id, name
        FROM habits
        WHERE user_id=$1
        AND is_active=true
        ORDER BY id
        """, user_id)

        confirmations_rows = await conn.fetch("""
        SELECT habit_id, DATE(datetime AT TIME ZONE $2) as day
        FROM confirmations
        WHERE user_id=$1
        AND datetime >= NOW() - INTERVAL '365 days'
        """, user_id, user_timezone)

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

    from zoneinfo import ZoneInfo

    today = datetime.now(
        ZoneInfo(user_timezone)
    ).date()

    today_str = today.isoformat()

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

        raw_series = []

        # 1 = подтверждение, 0 = пропуск
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            done = day in days
            raw_series.append(done)

        # стартовая точка
        level = 4
        series = []

        for done in raw_series:
            if done:
                level += 1
            else:
                level -= 1

            series.append({
                "value": level,
                "done": done
            })

# мягко сдвигаем график внутрь диапазона 1–7,
# но не ломаем направление вверх/вниз
        values = [p["value"] for p in series]

        min_value = min(values)
        max_value = max(values)

        if min_value < 1:
            shift = 1 - min_value
            for p in series:
                p["value"] += shift

        if max_value > 7:
            shift = max_value - 7
            for p in series:
                p["value"] -= shift

        habits.append({

            "id": hid,
            "name": name,
            "series": series,
            "streak": streak,
            "days": [d.isoformat() for d in days],
            "today": today_str,
            "confirmed_today": today in days

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
            COALESCE(u.avatar, 'avatar_1.png') as avatar,
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
            "avatar": r["avatar"],
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
    except Exception:
        data = {}

    init_data = data.get("initData")
    rating_type = data.get("ratingType", "global")

    if not init_data:
        return {
            "leaders": [],
            "me": None,
            "rating_type": rating_type
        }

    if rating_type not in ("global", "season"):
        rating_type = "global"

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    # ==========================================
    # СЕЗОННЫЙ РЕЙТИНГ
    # ==========================================

    if rating_type == "season":

        season_info = get_current_season_info()
        season_key = season_info["key"]

        async with pool.acquire() as conn:

            rows = await conn.fetch("""
                WITH ranked AS (
                    SELECT
                        u.user_id,

                        COALESCE(
                            u.nickname,
                            u.username,
                            u.first_name,
                            'Unknown'
                        ) AS username,

                        COALESCE(
                            u.avatar,
                            'avatar_1.png'
                        ) AS avatar,

                        COALESCE(
                            s.league,
                            'Бронза I'
                        ) AS league,

                        COALESCE(
                            ss.season_xp,
                            0
                        ) AS xp,

                        ROW_NUMBER() OVER (
                            ORDER BY
                                COALESCE(ss.season_xp, 0) DESC,
                                u.user_id ASC
                        ) AS rank

                    FROM users u

                    LEFT JOIN user_stats s
                        ON s.user_id = u.user_id

                    LEFT JOIN user_season_stats ss
                        ON ss.user_id = u.user_id
                        AND ss.season_key = $1
                )

                SELECT *
                FROM ranked
                ORDER BY rank
                LIMIT 100
            """, season_key)

            my = await conn.fetchrow("""
                WITH ranked AS (
                    SELECT
                        u.user_id,

                        COALESCE(
                            u.nickname,
                            u.username,
                            u.first_name,
                            'You'
                        ) AS username,

                        COALESCE(
                            u.avatar,
                            'avatar_1.png'
                        ) AS avatar,

                        COALESCE(
                            s.league,
                            'Бронза I'
                        ) AS league,

                        COALESCE(
                            ss.season_xp,
                            0
                        ) AS xp,

                        ROW_NUMBER() OVER (
                            ORDER BY
                                COALESCE(ss.season_xp, 0) DESC,
                                u.user_id ASC
                        ) AS rank

                    FROM users u

                    LEFT JOIN user_stats s
                        ON s.user_id = u.user_id

                    LEFT JOIN user_season_stats ss
                        ON ss.user_id = u.user_id
                        AND ss.season_key = $1
                )

                SELECT *
                FROM ranked
                WHERE user_id = $2
            """, season_key, user_id)

        leaders = []

        for row in rows:
            leaders.append({
                "user_id": row["user_id"],
                "rank": row["rank"],
                "avatar": row["avatar"],
                "username": row["username"],
                "league": row["league"],
                "xp": float(row["xp"])
            })

        return {
            "rating_type": "season",

            "season": {
                "key": season_info["key"],
                "number": season_info["number"],
                "name": season_info["name"],
                "year": season_info["year"],
                "start": season_info["start"].isoformat(),
                "end": season_info["end"].isoformat(),
                "days_left": season_info["days_left"]
            },

            "leaders": leaders,

            "me": {
                "rank": my["rank"] if my else None,
                "avatar": my["avatar"] if my else "avatar_1.png",
                "username": my["username"] if my else "You",
                "league": my["league"] if my else "Бронза I",
                "xp": float(my["xp"]) if my else 0
            }
        }

    # ==========================================
    # ГЛОБАЛЬНЫЙ РЕЙТИНГ
    # ==========================================

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
            SELECT
                u.user_id,
                u.last_global_rank,

                COALESCE(
                    u.nickname,
                    u.username,
                    u.first_name,
                    'Unknown'
                ) AS username,

                COALESCE(
                    u.avatar,
                    'avatar_1.png'
                ) AS avatar,

                COALESCE(
                    s.league,
                    'Бронза I'
                ) AS league,

                COALESCE(
                    s.xp,
                    0
                ) AS xp

            FROM users u

            LEFT JOIN user_stats s
                ON s.user_id = u.user_id

            WHERE u.last_global_rank IS NOT NULL

            ORDER BY u.last_global_rank
            LIMIT 100
        """)

        my = await conn.fetchrow("""
            SELECT
                u.last_global_rank,

                COALESCE(
                    u.nickname,
                    u.username,
                    u.first_name,
                    'You'
                ) AS username,

                COALESCE(
                    u.avatar,
                    'avatar_1.png'
                ) AS avatar,

                COALESCE(
                    s.league,
                    'Бронза I'
                ) AS league,

                COALESCE(
                    s.xp,
                    0
                ) AS xp

            FROM users u

            LEFT JOIN user_stats s
                ON s.user_id = u.user_id

            WHERE u.user_id = $1
        """, user_id)

    leaders = []

    for row in rows:
        leaders.append({
            "user_id": row["user_id"],
            "rank": row["last_global_rank"],
            "avatar": row["avatar"],
            "username": row["username"],
            "league": row["league"],
            "xp": float(row["xp"])
        })

    return {
        "rating_type": "global",
        "season": None,

        "leaders": leaders,

        "me": {
            "rank": my["last_global_rank"] if my else None,
            "avatar": my["avatar"] if my else "avatar_1.png",
            "username": my["username"] if my else "You",
            "league": my["league"] if my else "Бронза I",
            "xp": float(my["xp"]) if my else 0
        }
    }