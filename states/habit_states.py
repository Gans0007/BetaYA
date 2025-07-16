from aiogram.fsm.state import State, StatesGroup

class HabitForm(StatesGroup):
    name = State()
    days = State()
    description = State()

class ConfirmHabit(StatesGroup):
    waiting_for_media = State()
    waiting_for_selection = State()  # 👈 для подтверждения после медиа
