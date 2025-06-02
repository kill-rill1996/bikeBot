from aiogram.fsm.state import StatesGroup, State


class AddJobtype(StatesGroup):
    input_jobtype = State()
    select_categories = State()
    translate_1 = State()
    translate_2 = State()

