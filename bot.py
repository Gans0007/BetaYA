import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from init_db import init_db
from utils.reset_task import start_reset_scheduler
from routers_register import register_all_routers

# 🔧 Настройка логгирования
os.makedirs("logs", exist_ok=True)

# Основной лог-файл (всё подряд)
main_handler = logging.FileHandler("logs/bot.log", encoding='utf-8')
main_handler.setLevel(logging.INFO)

# Отдельный лог-файл для ошибок
error_handler = logging.FileHandler("logs/critical.log", encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# Консольный лог
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Регистрируем логгеры
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        main_handler,
        error_handler,
        console_handler
    ]
)

logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("📦 База данных инициализирована.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # 🔁 Регистрация всех роутеров
    await register_all_routers(dp)
    logger.info("🔁 Роутеры зарегистрированы.")

    # ⏰ Периодический сброс привычек
    asyncio.create_task(start_reset_scheduler(bot))
    logger.info("⏰ Планировщик сброса привычек запущен.")

    # 🚀 Запуск бота
    logger.info("🚀 Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
