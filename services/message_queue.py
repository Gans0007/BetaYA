# services/message_queue.py  СОЗДАЕТ ОЧЕРЕДЬ
import asyncio
import logging

QUEUE_CONFIRM = asyncio.Queue()

async def queue_consumer(process_func):
    while True:
        task = await QUEUE_CONFIRM.get()
        try:
            await process_func(task)
        except Exception as e:
            logging.error(f"[QUEUE ERROR] {e}")
        finally:
            QUEUE_CONFIRM.task_done()
