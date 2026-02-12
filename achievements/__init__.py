from .repository import AchievementRepository
from .service import AchievementService
from database import get_pool


async def setup_achievements(xp_service=None, money_service=None):
    pool = await get_pool()
    repo = AchievementRepository(pool)

    return AchievementService(
        repository=repo,
        xp_service=xp_service,
        money_service=money_service,
    )
