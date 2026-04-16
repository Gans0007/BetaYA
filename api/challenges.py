from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")  

    modules = []

    for level_key, challenges in CHALLENGES.items():

        module = {
            "level": level_key,
            "level_name": CHALLENGE_LEVELS["ru"][level_key],
            "challenges": []
        }

        for ch in challenges:
            ch_id, title, texts, _ = ch

            # 🔥 ВРЕМЕННО: у всех repeat_count = 0 (потом подключим БД)
            repeat_count = 0

            current_section = repeat_count + 1
            if current_section > 3:
                current_section = 3

            days_map = {1: 7, 2: 10, 3: 13}

            module["challenges"].append({
                "id": ch_id,
                "title": title,

                # 🔥 ТОЛЬКО ТЕКУЩИЙ УРОВЕНЬ
                "current_section": {
                    "section": current_section,
                    "days": days_map[current_section],
                    "stars": current_section,
                    "text": texts.get(current_section, "")
                }
            })

        modules.append(module)

    return {
        "modules": modules,

        # 🔥 временный прогресс (для визуала)
        "progress": {
            "level": "level_0",
            "challenge_id": "0_sleep_floor",
            "section": 1,
            "day": 3
        }
    }