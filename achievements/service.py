# achievements/service.py

from .definitions import ACHIEVEMENTS
from .registry import OPERATORS


class AchievementService:
    def __init__(self, repository, xp_service=None, money_service=None):
        self.repo = repository
        self.xp_service = xp_service
        self.money_service = money_service

    async def check(self, user_id: int, event: str, context: dict):
        for ach_id, ach in ACHIEVEMENTS.items():

            if ach["event"] != event:
                continue

            value = context.get(ach["metric"])
            operator_fn = OPERATORS[ach["operator"]]

            if not operator_fn(value, ach["target"]):
                continue

            if await self.repo.is_unlocked(user_id, ach_id):
                continue

            # фиксируем достижение
            await self.repo.unlock(user_id, ach_id)

            # награды (позже подключим)
            if self.xp_service and ach.get("xp", 0) > 0:
                await self.xp_service.add_xp(user_id, ach["xp"])

            if self.money_service and ach.get("money", 0) > 0:
                await self.money_service.add_money(user_id, ach["money"])
