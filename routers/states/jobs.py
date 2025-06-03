from aiogram.fsm.state import StatesGroup, State


class AddJobtype(StatesGroup):
    input_jobtype = State()
    select_categories = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


class EditJobetype(StatesGroup):
    input_jobtype = State()
    input_new_jobtype_title = State()
    select_categories = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


