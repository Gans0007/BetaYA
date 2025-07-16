import aiosqlite
from config import DB_PATH
from datetime import datetime

async def reset_unconfirmed_habits(user_id: int):
    today = datetime.now().date().isoformat()
    dropped = []

    async with aiosqlite.connect(DB_PATH) as conn:
        # Выбираем только активные, не-челенджевые, обычные привычки
        async with conn.execute("""
            SELECT h.id, h.name
            FROM habits h
            WHERE h.user_id = ?
              AND h.confirm_type != 'wake_time'
              AND h.is_active = 1
              AND h.is_challenge = 0
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()

        for habit_id, name in rows:
            # Проверяем, была ли привычка подтверждена сегодня
            async with conn.execute("""
                SELECT 1 FROM confirmations
                WHERE user_id = ?
                  AND habit_id = ?
                  AND DATE(datetime) = ?
            """, (user_id, habit_id, today)) as cursor2:
                exists = await cursor2.fetchone()

            # Если не была подтверждена — сбрасываем
            if exists is None:
                await conn.execute("""
                    UPDATE habits SET done_days = 0 WHERE id = ?
                """, (habit_id,))
                dropped.append(name)

        await conn.commit()

    return dropped


async def reset_unconfirmed_challenges(user_id: int) -> list[str]:
    today = datetime.now().date().isoformat()
    dropped = []

    async with aiosqlite.connect(DB_PATH) as conn:
        # Только активные челленджи (habit с is_challenge = 1)
        async with conn.execute("""
            SELECT h.id, h.name
            FROM habits h
            WHERE h.user_id = ?
              AND h.is_active = 1
              AND h.is_challenge = 1
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()

        for challenge_id, name in rows:
            # Проверяем, был ли подтверждён этот челлендж сегодня
            async with conn.execute("""
                SELECT 1 FROM confirmations
                WHERE user_id = ?
                  AND habit_id = ?
                  AND DATE(datetime) = ?
            """, (user_id, challenge_id, today)) as cursor2:
                confirmed = await cursor2.fetchone()

            if confirmed is None:
                await conn.execute("""
                    UPDATE habits SET done_days = 0 WHERE id = ?
                """, (challenge_id,))
                dropped.append(name)

        await conn.commit()

    return dropped
