from aiogram.fsm.state import StatesGroup, State


class AddTransportCategoryFSM(StatesGroup):
    input_name = State()
    input_emoji = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


class EditCategoryFSM(StatesGroup):
    input_title = State()
    input_emoji = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


class AddSubCategory(StatesGroup):
    input_subcategory = State()
    confirm = State()



