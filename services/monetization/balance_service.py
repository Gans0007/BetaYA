from db.db import database


async def get_user_balance_and_history(user_id: int) -> tuple[float, int, list[dict]]:
    # Получаем текущий баланс
    user_row = await database.fetch_one("""
        SELECT usdt_balance, xp_balance FROM users WHERE user_id = :user_id
    """, {"user_id": user_id})

    usdt, xp = user_row["usdt_balance"], user_row["xp_balance"] if user_row else (0.0, 0)

    # Получаем последние 6 записей истории
    history_rows = await database.fetch_all("""
        SELECT amount, type, reason, TO_CHAR(timestamp, 'DD.MM') as date
        FROM reward_history
        WHERE user_id = :user_id
        ORDER BY timestamp DESC
        LIMIT 6
    """, {"user_id": user_id})

    history = [
        {
            "amount": row["amount"],
            "type": row["type"],
            "reason": row["reason"],
            "date": row["date"]
        }
        for row in history_rows
    ]

    return usdt, xp, history
