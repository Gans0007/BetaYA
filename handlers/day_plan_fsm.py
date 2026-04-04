from aiogram.fsm.state import StatesGroup, State

class AddTaskFSM(StatesGroup):
    waiting_for_text = State()