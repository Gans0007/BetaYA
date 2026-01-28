# services/message_queue.py
import asyncio
import logging

from core.shutdown import shutdown_event

QUEUE_CONFIRM = asyncio.Queue()

async def queue_consumer(process_func, bot):
    logging.info("[QUEUE] Consumer started")

    while not shutdown_event.is_set() or not QUEUE_CONFIRM.empty():
        try:
            # ⏳ ждём задачу, но с таймаутом
            task = await asyncio.wait_for(
                QUEUE_CONFIRM.get(),
                timeout=1
            )
        except asyncio.TimeoutError:
            continue

        try:
            await process_func(task, bot)
        except Exception as e:
            logging.error(f"[QUEUE ERROR] {e}", exc_info=True)
        finally:
            QUEUE_CONFIRM.task_done()

    logging.warning("[QUEUE] Consumer stopped (shutdown)")
