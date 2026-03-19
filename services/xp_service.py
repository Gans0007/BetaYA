from core.database import get_pool

from repositories.user_stats_repository import increment_xp

# XP за уровни челленджей
XP_LEVELS = {
    "0": 5.0,   # Новичок
    "1": 6.0,   # Активность
    "2": 7.0,   # Фокус и энергия
    "3": 8.0,   # Самодисциплина
    "4": 9.0,   # Преодоление
}

# XP за сложность привычек
XP_DIFFICULTY = {
    1: 5.0,   # ⭐ Легко
    2: 6.0,   # ⭐⭐ Средне
    3: 7.0,   # ⭐⭐⭐ Сложно
}


# ------------------------------------------
# Лиги и их условия + цитата
# ------------------------------------------
LEAGUES = [
    # 🟤 БРОНЗА
    {"name": "Бронза I", "emoji": "🥉", "stars": 0, "xp": 0, "icon": "league_15.png", "quote": "Начало пути. Дисциплина только зарождается."},
    {"name": "Бронза II", "emoji": "🥉", "stars": 2, "xp": 100, "icon": "league_1.png", "quote": "Ты уже не стоишь на месте."},
    {"name": "Бронза III", "emoji": "🥉", "stars": 5, "xp": 300, "icon": "league_1.png", "quote": "Появляется ритм и первые результаты."},
    {"name": "Бронза IV", "emoji": "🥉", "stars": 10, "xp": 700, "icon": "league_1.png", "quote": "Ты начинаешь контролировать себя."},
    {"name": "Бронза V", "emoji": "🥉", "stars": 18, "xp": 1400, "icon": "league_1.png", "quote": "Ты уже не слабый игрок."},

    # ⚪ СЕРЕБРО
    {"name": "Серебро I", "emoji": "🥈", "stars": 28, "xp": 2500, "icon": "league_1.png", "quote": "Дисциплина становится нормой."},
    {"name": "Серебро II", "emoji": "🥈", "stars": 40, "xp": 4000, "icon": "league_1.png", "quote": "Ты уже отличаешься от большинства."},
    {"name": "Серебро III", "emoji": "🥈", "stars": 50, "xp": 5200, "icon": "league_1.png", "quote": "Ты держишь систему."},
    {"name": "Серебро IV", "emoji": "🥈", "stars": 60, "xp": 6000, "icon": "league_1.png", "quote": "Стабильность — твоя сила."},
    {"name": "Серебро V", "emoji": "🥈", "stars": 70, "xp": 7000, "icon": "league_1.png", "quote": "Ты почти на другом уровне."},

    # 🟡 ЗОЛОТО
    {"name": "Золото I", "emoji": "🥇", "stars": 85, "xp": 8500, "icon": "league_1.png", "quote": "Ты уже элита."},
    {"name": "Золото II", "emoji": "🥇", "stars": 100, "xp": 10000, "icon": "league_1.png", "quote": "Ты управляешь собой."},
    {"name": "Золото III", "emoji": "🥇", "stars": 120, "xp": 12000, "icon": "league_1.png", "quote": "Ты создаёшь правила."},
    {"name": "Золото IV", "emoji": "🥇", "stars": 140, "xp": 14000, "icon": "league_1.png", "quote": "Ты доминируешь."},
    {"name": "Золото V", "emoji": "🥇", "stars": 160, "xp": 17000, "icon": "league_1.png", "quote": "Максимум. Ты система."},
]

def get_league_by_name(name: str):
    return next((l for l in LEAGUES if l["name"] == name), LEAGUES[0])

async def add_xp_for_confirmation(conn, user_id: int, habit_id: int):
    """
    Начисляет XP за уникальное подтверждение.
    Работает внутри существующей транзакции.
    """

    # ------------------------------------------
    # 🔒 1) Проверка анти-фарма XP
    # ------------------------------------------
    count_today = await conn.fetchval("""
        SELECT COUNT(DISTINCT habit_id)
        FROM confirmations
        WHERE user_id = $1
          AND DATE(datetime AT TIME ZONE 'Europe/Kyiv') = CURRENT_DATE
    """, user_id)

    if count_today >= 3:
        return 0

    # ------------------------------------------
    # 2) Получаем данные привычки
    # ------------------------------------------
    habit = await conn.fetchrow("""
        SELECT is_challenge, challenge_id, difficulty
        FROM habits
        WHERE id = $1
    """, habit_id)

    if not habit:
        return 0

    # ------------------------------------------
    # 3) Определяем XP
    # ------------------------------------------
    if habit["is_challenge"]:
        level_key = habit["challenge_id"][0]
        xp_gain = XP_LEVELS.get(level_key, 1.0)
    else:
        diff = habit["difficulty"] or 1
        xp_gain = XP_DIFFICULTY.get(diff, 1.0)

    # ------------------------------------------
    # 4) Начисляем XP
    # ------------------------------------------
    await increment_xp(conn, user_id, xp_gain)

    return xp_gain



# ------------------------------------------
# 🔥 Централизованная проверка возможности повышения лиги
# ------------------------------------------
async def check_next_league(user_id: int):
    """
    Проверяет, доступна ли следующая лига.
    Возвращает:
    {
        "can_level_up": bool,
        "current_league": str,
        "next_league": dict | None,
        "need_stars": int,
        "need_xp": float
    }
    """

    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT 
                COALESCE(s.xp, 0) as xp,
                COALESCE(s.total_stars, 0) as total_stars,
                COALESCE(s.league, 'Бронза I') as league
            FROM users u
            LEFT JOIN user_stats s ON s.user_id = u.user_id
        WHERE u.user_id = $1
    """, user_id)

    if not user:
        return {"can_level_up": False, "next_league": None}

    xp_user = float(user["xp"])
    stars_user = int(user["total_stars"])
    current_league = user["league"]

    # индекс текущей лиги
    idx = next((i for i, l in enumerate(LEAGUES) if l["name"] == current_league), 0)

    # последняя лига
    if idx >= len(LEAGUES) - 1:
        return {
            "can_level_up": False,
            "current_league": current_league,
            "next_league": None,
            "need_stars": 0,
            "need_xp": 0
        }

    next_l = LEAGUES[idx + 1]

    need_stars = max(0, next_l["stars"] - stars_user)
    need_xp = max(0, next_l["xp"] - xp_user)

    can_level_up = (need_stars == 0 and need_xp == 0)

    return {
        "can_level_up": can_level_up,
        "current_league": current_league,
        "next_league": next_l,
        "need_stars": need_stars,
        "need_xp": need_xp,
    }

# ------------------------------------------
# 🏆 Начисление XP за достижения
# ------------------------------------------
async def add_xp_for_achievements(user_id: int, amount: float):
    """
    Начисляет XP за достижения.
    Отдельно от XP за подтверждение привычек.
    """

    pool = await get_pool()

    async with pool.acquire() as conn:
        await increment_xp(conn, user_id, amount)

