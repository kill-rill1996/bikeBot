from aiogram.fsm.state import StatesGroup, State


class MyWorksCustom(StatesGroup):
    period = State()
    end_date = State()