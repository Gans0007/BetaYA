# repositories/confirmations_repository.py

async def count_unique_confirm_days(conn, user_id: int) -> int:
    """
    Считает количество уникальных дат подтверждений
    внутри текущей транзакции.
    """
    val = await conn.fetchval("""
        SELECT COUNT(DISTINCT DATE(datetime))
        FROM confirmations
        WHERE user_id = $1
          AND (confirmed = TRUE OR confirmed IS NULL)
    """, user_id)
    return val or 0

