from aiogram.fsm.state import State, StatesGroup

class UploadVideoFSM(StatesGroup):
    waiting_for_video_link = State()