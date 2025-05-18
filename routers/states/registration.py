from aiogram.fsm.state import StatesGroup, State


class RegUsersFSM(StatesGroup):
    lang = State()
    username = State()
