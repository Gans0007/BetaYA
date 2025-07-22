import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from init_pg_db import init_postgres_db
from utils.reset_task import start_reset_scheduler
from routers_register import register_all_routers
from middlewares.db import DatabaseMiddleware
from services.reminder import reminder  # <-- импорт внизу, но до использования

from db.db import database

os.makedirs("logs", exist_ok=True)

# 📄 Настройка логов (если у тебя ещё не настроено)
logging.basicConfig(level=logging.INFO)

# ✅ Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📄 Обычный лог — INFO и выше
main_handler = logging.FileHandler("logs/bot.log", encoding='utf-8')
main_handler.setLevel(logging.INFO)

# ❗ Критический лог — только ERROR и выше
error_handler = logging.FileHandler("logs/critical.log", encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# 🖥️ Консоль — всё от INFO и выше
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 🎯 Общий формат
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
main_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 🔧 Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    handlers=[main_handler, error_handler, console_handler]
)

logger = logging.getLogger(__name__)

# ✅ Dispatcher СОЗДАЁМ ЗДЕСЬ (и только здесь)
dp = Dispatcher()
# ✅ Добавляем middleware
dp.message.middleware(DatabaseMiddleware())
dp.callback_query.middleware(DatabaseMiddleware())

async def main():
    # 🔌 Подключение к PostgreSQL
    await database.connect()
    logger.info("📦 Подключение к PostgreSQL установлено.")

    await init_postgres_db()  # можно временно отключить, если переводишь всё вручную

    # ✅ Бот и диспетчер уже созданы выше
    # 🔔 Напоминания
    asyncio.create_task(reminder.scheduled_reminder_loop(bot))

    await register_all_routers(dp)
    logger.info("🔁 Роутеры зарегистрированы.")

    asyncio.create_task(start_reset_scheduler(bot))
    logger.info("⏰ Планировщик сброса привычек запущен.")

    logger.info("🚀 Бот запущен.")
    await dp.start_polling(bot)

    # 🔌 Отключение от базы
    await database.disconnect()
    logger.info("📴 PostgreSQL отключён.")

if __name__ == "__main__":
    asyncio.run(main())
