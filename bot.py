import asyncio
import logging
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

    # 2) Подключение к БД (asyncpg pool)
    await create_pool()

    # 3) Инициализация схемы БД
    await create_users_table()
    logging.info("✅ Database connected and schema ensured")

    # 4) Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(add_habit_router)
    dp.include_router(challenges_router)
    dp.include_router(add_custom_habit_router)
    dp.include_router(confirm_habit_handler.router)
    dp.include_router(active_tasks_handler.router)

    logging.info("🤖 Bot started...")
    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()
        await bot.session.close()
        logging.info("🛑 Bot stopped, pool closed.")

if __name__ == "__main__":
    asyncio.run(main())
