#handlers/profile/__init__.py
from .menu import router as menu_router
from .achievements import router as achievements_router
from .settings import router as settings_router
from .settings_timezone import router as settings_timezone_router
from .stats import router as stats_router
from .affiliate import router as affiliate_router


def setup(dp):
    dp.include_router(menu_router)
    dp.include_router(achievements_router)
    dp.include_router(settings_router)
    dp.include_router(settings_timezone_router)
    dp.include_router(stats_router)
    dp.include_router(affiliate_router)

    print("✅ PROFILE module loaded")
