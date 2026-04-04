import asyncio
import logging
import signal
from contextlib import suppress

from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN

from core import (
    shutdown_event,
    startup,
    shutdown,
)

from handlers.start_handler import router as start_router
from handlers.add_habit_handler import router as add_habit_router
from handlers.challenges_handler import router as challenges_router
from handlers.add_custom_habit_handler import router as add_custom_habit_router
from handlers import confirm_habit_handler
from handlers import active_tasks_handler
from handlers.profile import setup as setup_profile
from handlers.honor_handler import router as honor_router
from handlers.subscription_handler import router as subscription_router
from handlers.habit_reminder_handler import router as habit_reminder_router
from handlers.day_plan import router as day_plan_router

from tasks.habit_reminder_tasks import habit_reminder_task
from tasks.habit_reset_task import check_habit_resets
from tasks.challenge_reset_task import check_challenge_resets
from tasks.honor_global_task import honor_global_rank_daily

from middlewares.subscription_middleware import SubscriptionMiddleware
from services.message_queue import queue_consumer, QUEUE_CONFIRM

from fastapi import FastAPI
import uvicorn
import asyncio

app = FastAPI()

from api.dashboard import router as dashboard_router
app.include_router(dashboard_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


# -------------------------------------------------
# 🔹 Graceful shutdown handler
# -------------------------------------------------
def setup_signal_handlers(loop):
    for sig in (signal.SIGTERM, signal.SIGINT):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, shutdown_event.set)


# -------------------------------------------------
# 🔹 Background tasks launcher
# -------------------------------------------------
async def start_background_tasks(bot):
    from tasks.daily_reminder_task import send_daily_reminders
    from handlers.confirm_habit_handler import process_task_from_queue
    from tasks.subscription_check_task import subscription_checker

    tasks = []

    tasks.append(asyncio.create_task(honor_global_rank_daily(bot)))
    tasks.append(asyncio.create_task(check_challenge_resets(bot)))
    tasks.append(asyncio.create_task(check_habit_resets(bot)))
    tasks.append(asyncio.create_task(habit_reminder_task(bot)))
    tasks.append(asyncio.create_task(send_daily_reminders(bot)))
    tasks.append(asyncio.create_task(queue_consumer(process_task_from_queue, bot)))
    tasks.append(asyncio.create_task(subscription_checker(bot)))

    return tasks


# -------------------------------------------------
# 🔹 Main
# -------------------------------------------------
async def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан")

    loop = asyncio.get_running_loop()
    setup_signal_handlers(loop)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
    ])

    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # Routers
    dp.include_router(start_router)
    dp.include_router(add_habit_router)
    dp.include_router(challenges_router)
    dp.include_router(add_custom_habit_router)
    dp.include_router(confirm_habit_handler.router)
    dp.include_router(active_tasks_handler.router)
    dp.include_router(day_plan_router)
    setup_profile(dp)
    dp.include_router(honor_router)
    dp.include_router(subscription_router)
    dp.include_router(habit_reminder_router)

    # --- STARTUP ---
    background_tasks = await startup(bot, start_background_tasks)

    logging.info("🤖 Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await shutdown(bot, background_tasks, QUEUE_CONFIRM)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())
