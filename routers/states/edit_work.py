from aiogram.fsm.state import StatesGroup, State


class EditWorkFSM(StatesGroup):
    enter_comment = State()
    confirm = State()



