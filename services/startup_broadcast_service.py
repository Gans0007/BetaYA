import logging
from aiogram import Bot
from database import get_pool

logger = logging.getLogger(__name__)

CHAT_LINK = "https://t.me/yourambitions_chat"


async def send_startup_message(bot: Bot):
    pool = await get_pool()

    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT user_id FROM users")

    logger.info(f"[STARTUP_BROADCAST] Отправка сообщения {len(users)} пользователям")

    for row in users:
        user_id = row["user_id"]

        try:
            await bot.send_message(
                user_id,
                (
                    "💬 <b>У нас есть общий чат комьюнити</b>\n"
                    "Там общение, поддержка и движение вперёд 💪\n\n"
                    "👉 <a href=\"https://t.me/yourambitions_chat\">Вступить в чат</a>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(
                f"[STARTUP_BROADCAST] Не удалось отправить сообщение пользователю {user_id}: {e}"
            )
