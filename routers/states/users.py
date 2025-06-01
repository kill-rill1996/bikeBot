from aiogram.fsm.state import StatesGroup, State


class AddUserFSM(StatesGroup):
    tg_id = State()
    username = State()
    role = State()
    confirmation = State()
