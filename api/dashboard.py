from fastapi import APIRouter, Request, HTTPException
from api.main import validate_telegram_data, app

router = APIRouter()


@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    user_id = validate_telegram_data(init_data)

    async with app.state.pool.acquire() as conn:

        habits = await conn.fetch(
            """
            SELECT name
            FROM habits
            WHERE user_id = $1
            AND is_active = TRUE
            ORDER BY created_at
            """,
            user_id
        )

    return {
        "habits": [dict(h) for h in habits]
    }