# achievements/repository.py

class AchievementRepository:
    def __init__(self, pool):
        self.pool = pool

    async def is_unlocked(self, user_id: int, achievement_id: str) -> bool:
        query = """
        SELECT 1 FROM user_achievements
        WHERE user_id = $1 AND achievement_id = $2
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, achievement_id)
            return row is not None

    async def unlock(self, user_id: int, achievement_id: str):
        query = """
        INSERT INTO user_achievements (user_id, achievement_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, achievement_id)
