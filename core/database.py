import asyncpg
from config import DATABASE_URL

pool = None

async def create_pool():
    global pool
    if pool is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL не задан. Проверь .env")
        pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=25,
            command_timeout=60
        )
        print("✅ Database pool created")

async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None
        print("🔒 Database pool closed")

async def get_pool():
    global pool
    if pool is None:
        raise RuntimeError("Database pool is not initialized! Call create_pool() first.")
    return pool
