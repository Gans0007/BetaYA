from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS

from repositories.challenge_repository import (
    get_completed_challenges,
    get_active_challenges
)

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    # 🔥 пока без парсинга Telegram (упрощенно)
    user_id = 0

    # 🔥 завершенные (звезды)
    completed_rows = await get_completed_challenges(user_id)
    completed_map = {
        row["challenge_id"]: row["repeat_count"]
        for row in completed_rows
    }

    # 🔥 активные челленджи (прогресс)
    active_rows = await get_active_challenges(user_id)
    active_map = {
        row["challenge_id"]: row
        for row in active_rows
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

            # ⭐ звезды
            repeat_count = completed_map.get(ch_id, 0)

            current_section = repeat_count + 1
            if current_section > 3:
                current_section = 3

            days_map = {1: 7, 2: 10, 3: 13}

            # 🔥 активный челлендж
            active = active_map.get(ch_id)

            done_days = active["done_days"] if active else 0
            total_days = active["days"] if active else days_map[current_section]

            module["challenges"].append({
                "id": ch_id,
                "title": title,

                "current_section": {
                    "section": current_section,
                    "days": total_days,
                    "stars": current_section,
                    "text": texts.get(current_section, "")
                },

                # 🔥 прогресс
                "progress": {
                    "done_days": done_days,
                    "is_active": True if active else False
                }
            })

        modules.append(module)

    return {
        "modules": modules
    }