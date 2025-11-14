from database import get_pool

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

async def add_xp_for_confirmation(user_id: int, habit_id: int):
    """Начисляет XP за уникальное подтверждение привычки/челленджа."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Получаем данные привычки
        habit = await conn.fetchrow("""
            SELECT is_challenge, challenge_id, difficulty
            FROM habits
            WHERE id = $1
        """, habit_id)

        if not habit:
            return  # привычки нет → XP не начисляем

        # ------------------------------------------
        # 1) ЧЕЛЛЕНДЖ → XP по уровню
        # ------------------------------------------
        if habit["is_challenge"]:
            level_key = habit["challenge_id"][0]
            xp_gain = XP_LEVELS.get(level_key, 1.0)

        # ------------------------------------------
        # 2) ПРИВЫЧКА → XP по сложности
        # ------------------------------------------
        else:
            diff = habit["difficulty"] or 1
            xp_gain = XP_DIFFICULTY.get(diff, 1.0)

        # ------------------------------------------
        # Начисляем XP пользователю
        # ------------------------------------------
        await conn.execute("""
            UPDATE users
            SET xp = xp + $1
            WHERE user_id = $2
        """, xp_gain, user_id)

        return xp_gain
