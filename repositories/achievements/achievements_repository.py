from core.database import get_pool


# -------------------------------------------------
# Проверка: есть ли уже достижение у пользователя
# -------------------------------------------------
async def has_user_achievement(conn, user_id: int, achievement_code: str) -> bool:
    result = await conn.fetchrow("""
        SELECT 1
        FROM user_achievements
        WHERE user_id = $1
          AND achievement_code = $2
    """, user_id, achievement_code)

    return result is not None


# -------------------------------------------------
# Выдать достижение пользователю
# -------------------------------------------------
async def grant_achievement(conn, user_id: int, achievement_code: str):
    await conn.execute("""
        INSERT INTO user_achievements (user_id, achievement_code)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
    """, user_id, achievement_code)


async def get_user_achievements_codes(conn, user_id: int):
    rows = await conn.fetch("""
        SELECT achievement_code
        FROM user_achievements
        WHERE user_id = $1
    """, user_id)

    return {row["achievement_code"] for row in rows}