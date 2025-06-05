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


class AddJob(StatesGroup):
    select_category = State()
    select_jobtype = State()
    input_job_title = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()


class EditJob(StatesGroup):
    select_category = State()
    select_jobtype = State()
    select_job = State()
    input_job_title = State()
    translate_1 = State()
    translate_2 = State()
    confirm = State()

