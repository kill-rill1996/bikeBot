from aiogram.fsm.state import StatesGroup, State


class AddTransportCategoryFSM(StatesGroup):
    input_name = State()
    input_emoji = State()
    confirm = State()

