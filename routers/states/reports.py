from aiogram.fsm.state import StatesGroup, State


class IndividualMechanicReport(StatesGroup):
    period = State()
    end_date = State()
    report = State()


class SummaryMechanicReport(StatesGroup):
    period = State()
    report = State()


class TransportReport(StatesGroup):
    period = State()
    report = State()


class JobTypesReport(StatesGroup):
    period = State()
    report = State()


class InefficiencyReport(StatesGroup):
    period = State()
    report = State()


class LocationReport(StatesGroup):
    period = State()
    report = State()