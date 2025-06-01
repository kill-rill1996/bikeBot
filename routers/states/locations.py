from aiogram.fsm.state import StatesGroup, State


class AddLocationFSM(StatesGroup):
    input_name = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


class EditLocationFSM(StatesGroup):
    input_name = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()