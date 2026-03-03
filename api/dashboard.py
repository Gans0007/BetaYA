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
            SELECT 
                current_streak,
                COALESCE(ROUND(xp),0) as xp,

                CASE
                    WHEN COALESCE(xp,0) >= 6000 THEN 'Созидатель'
                    WHEN COALESCE(xp,0) >= 5200 THEN 'Непоколебимый'
                    WHEN COALESCE(xp,0) >= 4000 THEN 'Лидер примера'
                    WHEN COALESCE(xp,0) >= 2500 THEN 'Железный характер'
                    WHEN COALESCE(xp,0) >= 1400 THEN 'Ответственный'
                    WHEN COALESCE(xp,0) >= 700 THEN 'Ученик дисциплины'
                    WHEN COALESCE(xp,0) >= 300 THEN 'Новичок'
                    WHEN COALESCE(xp,0) >= 100 THEN 'Сомневающийся'
                    ELSE 'Безответственный'
                END as league

            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

    return {
        "telegram_user_id": user_id,
        "db_row": dict(row) if row else None
    }