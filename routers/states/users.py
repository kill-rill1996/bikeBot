from aiogram.fsm.state import StatesGroup, State


class AddUserFSM(StatesGroup):
    tg_id = State()
    confirmation = State()


class EditUsernameFSM(StatesGroup):
    username = State()
    confirmation = State()


class EditRoleFSM(StatesGroup):
    role = State()
    confirmation = State()