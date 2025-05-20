from aiogram.fsm.state import StatesGroup, State


class AddWorkFSM(StatesGroup):
    vehicle_category = State()
    vehicle_subcategory = State()
    vehicle_number = State()
    work_category = State()
