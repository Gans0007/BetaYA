from aiogram import Dispatcher
from handlers.complete_habit_handler import router as complete_router
from handlers import balance_handler
from handlers import referral_handler
from handlers import upload_video
from handlers.full_version_handler import router as full_version_router
from handlers.example_video import router as example_video_router
from middlewares.antispam import AntiSpamMiddleware

from handlers import (
    start,
    habit_add,
    challenge_select,
    habit_confirm,
    habit_auto_confirm,
    delete_habit
)
from keyboards import menu

async def register_all_routers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(full_version_router)
    dp.include_router(menu.router)
    dp.include_router(habit_add.router)
    dp.include_router(challenge_select.router)
    dp.include_router(habit_confirm.router)
    dp.include_router(habit_auto_confirm.router)
    dp.include_router(delete_habit.router)
    dp.include_router(complete_router)
    dp.include_router(balance_handler.router)
    dp.include_router(referral_handler.router)
    dp.include_router(upload_video.router)
    dp.include_router(example_video_router)
    dp.update.middleware(AntiSpamMiddleware(delay=1))
