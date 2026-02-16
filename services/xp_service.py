from core.database import get_pool
from aiogram import Bot
from config import BOT_TOKEN  # если токен у тебя в другом месте — укажи путь
bot = Bot(token=BOT_TOKEN)

# XP за уровни челленджей
XP_LEVELS = {
    "0": 1.0,   # Новичок
    "1": 1.2,   # Активность
    "2": 1.4,   # Фокус и энергия
    "3": 1.6,   # Самодисциплина
    "4": 1.8,   # Преодоление
}

# XP за сложность привычек
XP_DIFFICULTY = {
    1: 1.0,   # ⭐ Легко
    2: 1.3,   # ⭐⭐ Средне
    3: 1.6,   # ⭐⭐⭐ Сложно
}


# ------------------------------------------
# Лиги и их условия + цитата
# ------------------------------------------
LEAGUES = [
    {
        "name": "Безответственный",
        "emoji": "🕳️",
        "stars": 0,
        "xp": 0,
        "quote": "Поглощён ленью и оправданиями. Всё время «потом». Начало пути — ноль осознанности."
    },
    {
        "name": "Сомневающийся",
        "emoji": "🌫️",
        "stars": 2,
        "xp": 50,
        "quote": "Хочет меняться, но туман сомнений мешает видеть путь."
    },
    {
        "name": "Новичок",
        "emoji": "🌱",
        "stars": 5,
        "xp": 150,
        "quote": "Сделал первый шаг. Маленький росток через бетон привычек."
    },
    {
        "name": "Ученик дисциплины",
        "emoji": "🔥",
        "stars": 10,
        "xp": 350,
        "quote": "Учится терпению и контролю. Уже чувствует вкус победы над собой."
    },
    {
        "name": "Ответственный",
        "emoji": "🛡️",
        "stars": 20,
        "xp": 700,
        "quote": "Держит слово. Делает, даже когда не хочется."
    },
    {
        "name": "Железный характер",
        "emoji": "⚔️",
        "stars": 35,
        "xp": 1200,
        "quote": "Не сдаётся. Каждый день — как бой с самим собой."
    },
    {
        "name": "Лидер примера",
        "emoji": "🦁",
        "stars": 55,
        "xp": 2000,
        "quote": "Действиями вдохновляет других. Лидер — не по словам, а по поступкам."
    },
    {
        "name": "Непоколебимый",
        "emoji": "🪨",
        "stars": 80,
        "xp": 3000,
        "quote": "Никакие обстоятельства не могут сбить с курса."
    },
    {
        "name": "Мастер контроля",
        "emoji": "🧘‍♂️",
        "stars": 110,
        "xp": 4500,
        "quote": "Контролирует разум, тело и эмоции. Спокоен внутри — мощен снаружи."
    },
    {
        "name": "Созидатель",
        "emoji": "🌅",
        "stars": 150,
        "xp": 6500,
        "quote": "Создает, а не разрушает. Ведёт, вдохновляет, созидает новый мир."
    },
]

async def add_xp_for_confirmation(user_id: int, habit_id: int):
    """Начисляет XP за уникальное подтверждение привычки/челленджа с ограничением:
       — не более 3 уникальных подтверждений в сутки дают XP.
    """

    pool = await get_pool()

    async with pool.acquire() as conn:

        # ------------------------------------------
        # 🔒 1) Проверка анти-фарма XP
        #     Сколько уникальных привычек подтверждено сегодня?
        # ------------------------------------------
        count_today = await conn.fetchval("""
            SELECT COUNT(DISTINCT habit_id)
            FROM confirmations
            WHERE user_id = $1
              AND DATE(datetime AT TIME ZONE 'Europe/Kyiv') = CURRENT_DATE
        """, user_id)

        # Если уже 3 уникальных → XP не начисляем
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
            return 0  # Привычки нет → XP не даём

        # ------------------------------------------
        # 3) Челлендж → XP по уровню
        # ------------------------------------------
        if habit["is_challenge"]:
            level_key = habit["challenge_id"][0]
            xp_gain = XP_LEVELS.get(level_key, 1.0)

        # ------------------------------------------
        # 4) Привычка → XP по сложности
        # ------------------------------------------
        else:
            diff = habit["difficulty"] or 1
            xp_gain = XP_DIFFICULTY.get(diff, 1.0)

        # ------------------------------------------
        # 5) Начисляем XP пользователю
        # ------------------------------------------
        await conn.execute("""
            UPDATE users
            SET xp = xp + $1
            WHERE user_id = $2
        """, xp_gain, user_id)

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
            SELECT xp, total_stars, league
            FROM users
            WHERE user_id = $1
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

