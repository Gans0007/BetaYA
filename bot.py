import asyncio
import logging
from aiogram import types
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import create_pool, close_pool
from init_pg_db import create_users_table

# Роутеры
from handlers.start_handler import router as start_router
from handlers.add_habit_handler import router as add_habit_router
from handlers.challenges_handler import router as challenges_router
from handlers.add_custom_habit_handler import router as add_custom_habit_router
from handlers import confirm_habit_handler
from handlers import active_tasks_handler 
from handlers.profile_menu_handler import router as profile_menu_router
from handlers.profile_settings_handler import router as profile_settings_router
from handlers.profile_stats_handler import router as profile_stats_router
from challenge_reset_task import check_challenge_resets
from handlers.honor_handler import router as honor_router
from habit_reset_task import check_habit_resets
from middlewares.subscription_middleware import SubscriptionMiddleware
from handlers.subscription_handler import router as subscription_router

from handlers.affiliate_menu_handler import router as affiliate_menu_router

from honor_global_task import honor_global_rank_daily

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Проверь .env")

    # 1) Бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
    ])

    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # 2) Подключение к БД (asyncpg pool)
    await create_pool()

    # 3) Инициализация схемы БД
    await create_users_table()
    logging.info("✅ Database connected and schema ensured")

    asyncio.create_task(honor_global_rank_daily(bot))

    # 4) Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(add_habit_router)
    dp.include_router(challenges_router)
    dp.include_router(add_custom_habit_router)
    dp.include_router(confirm_habit_handler.router)
    dp.include_router(active_tasks_handler.router)
    dp.include_router(profile_menu_router)
    dp.include_router(profile_settings_router)
    dp.include_router(profile_stats_router)
    dp.include_router(honor_router)
    dp.include_router(affiliate_menu_router)
    dp.include_router(subscription_router)

    # 5) Запускаем фоновые задачи
    from daily_reminder_task import send_daily_reminders
    asyncio.create_task(send_daily_reminders(bot))

    # 6) очередь отправки
    from services.message_queue import queue_consumer
    from handlers.confirm_habit_handler import process_task_from_queue
    asyncio.create_task(queue_consumer(process_task_from_queue))

    # 🆕 Проверка подписки
    from subscriprion_check_task import subscription_checker
    asyncio.create_task(subscription_checker())

    # 🔥 Запускаем автоматическую проверку аннулирований (челленджи + привычки)
    asyncio.create_task(check_challenge_resets())
    asyncio.create_task(check_habit_resets())

    logging.info("🤖 Bot started...")
    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()
        await bot.session.close()
        logging.info("🛑 Bot stopped, pool closed.")

if __name__ == "__main__":
    asyncio.run(main())
