from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.post("/api/dashboard")
async def get_dashboard(request: Request):
    data = await request.json()
    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    # TODO: здесь твоя validate_init_data(init_data)

    # Временно можно вернуть тест
    return {
        "xp": 125,
        "streak": 7,
        "league": "Silver",
        "weekly_xp": [10, 20, 15, 30, 5, 25, 20]
    }