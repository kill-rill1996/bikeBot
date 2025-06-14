from aiogram.fsm.state import StatesGroup, State


class DeleteWorkFSM(StatesGroup):
    operation_id = State()
    password = State()
    confirmation = State()
    second_confirmation = State()