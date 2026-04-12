# api/challenges.py

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

            module["challenges"].append({
                "id": ch_id,
                "title": title,
                "sections": [
                    {"section":1,"days":7,"stars":1,"text":texts.get(1,"")},
                    {"section":2,"days":10,"stars":2,"text":texts.get(2,"")},
                    {"section":3,"days":13,"stars":3,"text":texts.get(3,"")}
                ]
            })

        modules.append(module)

    return {
        "modules": modules,

        # тестовый прогресс
        "progress": {
            "level": "level_0",
            "challenge_id": "0_sleep_floor",
            "section": 1,
            "day": 3
        }
    }