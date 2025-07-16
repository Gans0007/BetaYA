
# Хранилище напоминаний (user_id, habit_id) -> asyncio.Task

_reminder_tasks = {}

def add_reminder(user_id: int, habit_id: int, task):
    _reminder_tasks[(user_id, habit_id)] = task

def remove_reminder(user_id: int, habit_id: int):
    task = _reminder_tasks.pop((user_id, habit_id), None)
    if task and not task.done():
        task.cancel()

def get_reminder(user_id: int, habit_id: int):
    return _reminder_tasks.get((user_id, habit_id))

def cancel_all_reminders():
    for task in _reminder_tasks.values():
        if not task.done():
            task.cancel()
    _reminder_tasks.clear()
