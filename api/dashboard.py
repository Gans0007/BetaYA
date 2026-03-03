from fastapi import APIRouter, Request, HTTPException
from api.main import validate_telegram_data, app

router = APIRouter()

@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    user_id = validate_telegram_data(init_data)

    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT current_streak
            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

    if not row:
        return {"streak": 0}

    return {
        "streak": row["current_streak"]
    }