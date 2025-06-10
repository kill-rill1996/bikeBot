from aiogram.fsm.state import StatesGroup, State


class SearchWorkFSM(StatesGroup):
    enter_search_data = State()
    select_transport = State()
    period = State()
    custom_period = State()
    end_date = State()
    works_list = State()
