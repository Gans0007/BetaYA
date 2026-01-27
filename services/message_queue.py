# services/message_queue.py
import asyncio
import logging

QUEUE_CONFIRM = asyncio.Queue()

async def queue_consumer(process_func, bot):
    logging.info("[QUEUE] Consumer started")

    while True:
        task = await QUEUE_CONFIRM.get()
        try:
            await process_func(task, bot)   # ✅ ПЕРЕДАЁМ BOT
        except Exception as e:
            logging.error(f"[QUEUE ERROR] {e}", exc_info=True)
        finally:
            QUEUE_CONFIRM.task_done()

