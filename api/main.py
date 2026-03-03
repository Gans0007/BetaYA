import asyncpg
from fastapi import FastAPI

app = FastAPI()
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT user_id, xp, current_streak FROM users WHERE user_id=$1",
            user_id
        )

    if not user:
        return {"error": "User not found"}

    return dict(user)