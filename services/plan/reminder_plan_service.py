import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from core.database import get_pool


async def plan_reminder_loop(bot):
    while True:
        try:
            now = datetime.now(ZoneInfo("Europe/Kyiv"))

            # Проверяем окно отправки, чтобы не пропустить 20:00
            if now.hour == 20 and now.minute in range(0, 5):
                print("⏰ PLAN REMINDER START")

                pool = await get_pool()

                async with pool.acquire() as conn:
                    users = await conn.fetch(
                        """
                        SELECT user_id
                        FROM plan_reminders
                        """
                    )

                for user in users:
                    user_id = user["user_id"]

                    try:
                        await bot.send_message(
                            user_id,
                            "🔥 Пора запланировать завтра!\n\n"
                            "Открой «План на завтра» и задай задачи 💪"
                        )

                        # Удаляем напоминание после успешной отправки,
                        # чтобы оно не приходило повторно каждый день
                        async with pool.acquire() as conn:
                            await conn.execute(
                                """
                                DELETE FROM plan_reminders
                                WHERE user_id = $1
                                """,
                                user_id
                            )

                        print(f"✅ Напоминание отправлено: {user_id}")

                    except Exception as e:
                        print(f"❌ Ошибка отправки {user_id}: {e}")

                # Защита от повторного запуска в пределах окна 20:00–20:04
                await asyncio.sleep(300)

        except Exception as e:
            print(f"❌ Ошибка в plan_reminder_loop: {e}")

        await asyncio.sleep(30)