from aiogram.fsm.state import StatesGroup, State


class StatisticsCustomPeriod(StatesGroup):
    period = State()
    end_date = State()