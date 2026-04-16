from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS

# 🔥 добавляем
from repositories.challenge_repository import get_completed_challenges

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    # потом сделаем нормальную валидацию
    user_id = 0

    # 🔥 получаем завершенные челленджи
    completed_rows = await get_completed_challenges(user_id)

    # {challenge_id: repeat_count}
    completed_map = {
        row["challenge_id"]: row["repeat_count"]
        for row in completed_rows
    }

    modules = []

    for level_key, challenges in CHALLENGES.items():

        module = {
            "level": level_key,
            "level_name": CHALLENGE_LEVELS["ru"][level_key],
            "challenges": []
        }

        for ch in challenges:
            ch_id, title, texts, _ = ch

            # 🔥 берем реальные звезды
            repeat_count = completed_map.get(ch_id, 0)

            current_section = repeat_count + 1
            if current_section > 3:
                current_section = 3

            days_map = {1: 7, 2: 10, 3: 13}

            module["challenges"].append({
                "id": ch_id,
                "title": title,

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

        # 🔥 пока оставляем тестовый прогресс
        "progress": {
            "level": "level_0",
            "challenge_id": "0_sleep_floor",
            "section": 1,
            "day": 3
        }
    }