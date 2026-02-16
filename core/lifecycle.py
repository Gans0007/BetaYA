import asyncio
import logging

from .database import create_pool, close_pool
from .init_pg_db import create_users_table
from .shutdown import shutdown_event


# ----------------------------
# STARTUP
# ----------------------------
async def startup(bot, start_background_tasks):
    await create_pool()
    await create_users_table()
    logging.info("✅ Database connected")

    background_tasks = await start_background_tasks(bot)
    return background_tasks


# ----------------------------
# SHUTDOWN
# ----------------------------
async def shutdown(bot, background_tasks, queue):
    logging.warning("🛑 Shutdown initiated")

    shutdown_event.set()

    logging.warning("🛑 Cancelling background tasks...")
    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)

    logging.warning("⏳ Waiting for queue to finish...")
    await queue.join()

    await close_pool()
    await bot.session.close()

    logging.warning("✅ Bot shutdown completed")
