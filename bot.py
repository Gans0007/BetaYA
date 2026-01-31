import asyncio
import logging
import signal
from contextlib import suppress

from core.shutdown import shutdown_event

from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from database import create_pool, close_pool
from init_pg_db import create_users_table

from handlers.start_handler import router as start_router
from handlers.add_habit_handler import router as add_habit_router
from handlers.challenges_handler import router as challenges_router
from handlers.add_custom_habit_handler import router as add_custom_habit_router
from handlers import confirm_habit_handler
from handlers import active_tasks_handler

from handlers.profile.menu import router as profile_menu_router
from handlers.profile.settings import router as profile_settings_router
from handlers.profile.stats import router as profile_stats_router
from handlers.profile.achievements import router as achievements_router
from handlers.profile.affiliate import router as affiliate_menu_router

from handlers.honor_handler import router as honor_router
from handlers.subscription_handler import router as subscription_router
from handlers.habit_reminder_handler import router as habit_reminder_router



from tasks.habit_reminder_tasks import habit_reminder_task


from middlewares.subscription_middleware import SubscriptionMiddleware
from habit_reset_task import check_habit_resets
from challenge_reset_task import check_challenge_resets
from honor_global_task import honor_global_rank_daily

from services.message_queue import queue_consumer, QUEUE_CONFIRM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def setup_signal_handlers(loop):
    for sig in (signal.SIGTERM, signal.SIGINT):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, shutdown_event.set)


async def main():
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

    await create_pool()
    await create_users_table()
    logging.info("✅ Database connected")

    # Routers
    dp.include_router(start_router)
    dp.include_router(add_habit_router)
    dp.include_router(challenges_router)
    dp.include_router(add_custom_habit_router)
    dp.include_router(confirm_habit_handler.router)
    dp.include_router(active_tasks_handler.router)
    dp.include_router(profile_menu_router)
    dp.include_router(achievements_router)
    dp.include_router(profile_settings_router)
    dp.include_router(profile_stats_router)
    dp.include_router(honor_router)
    dp.include_router(affiliate_menu_router)
    dp.include_router(subscription_router)
    dp.include_router(habit_reminder_router)

    # Background tasks
    asyncio.create_task(honor_global_rank_daily(bot))
    asyncio.create_task(check_challenge_resets(bot))
    asyncio.create_task(check_habit_resets(bot))
    asyncio.create_task(habit_reminder_task(bot))


    from daily_reminder_task import send_daily_reminders
    asyncio.create_task(send_daily_reminders(bot))

    from handlers.confirm_habit_handler import process_task_from_queue
    asyncio.create_task(queue_consumer(process_task_from_queue, bot))

    from subscriprion_check_task import subscription_checker
    asyncio.create_task(subscription_checker(bot))

    logging.info("🤖 Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        logging.warning("🛑 Shutdown initiated")

        shutdown_event.set()

        logging.warning("⏳ Waiting for queue to finish...")
        await QUEUE_CONFIRM.join()

        await close_pool()
        await bot.session.close()

        logging.warning("✅ Bot shutdown completed")


if __name__ == "__main__":
    asyncio.run(main())
