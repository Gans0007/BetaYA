# services/monetization/balance_service.py

import aiosqlite
from config import DB_PATH

async def get_user_balance_and_history(user_id: int) -> tuple[float, int, list[dict]]:
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем текущий баланс
        cursor = await db.execute(
            "SELECT usdt_balance, xp_balance FROM users WHERE user_id = ?",
            (user_id,)
        )
        user_row = await cursor.fetchone()
        usdt, xp = user_row if user_row else (0.0, 0)

        # Получаем последние 10 записей истории
        history_cursor = await db.execute(
            """
            SELECT amount, type, reason, strftime('%d.%m', timestamp) as date
            FROM reward_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 6
            """,
            (user_id,)
        )
        history_rows = await history_cursor.fetchall()

        history = [
            {
                "amount": row[0],
                "type": row[1],
                "reason": row[2],
                "date": row[3]
            }
            for row in history_rows
        ]

        return usdt, xp, history
