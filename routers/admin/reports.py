import datetime
from typing import Any

from routers.menu import show_main_menu
from schemas.operations import Operation, OperationAdd
from settings import settings

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from utils.translator import translator as t
from utils.validations import is_valid_vehicle_number, is_valid_duration
from routers.states.add_work import AddWorkFSM
from database.orm import AsyncOrm
from utils.date_time_service import convert_date_time

from routers.keyboards import admin as kb

router = Router()


@router.callback_query(F.data == "admin|reports")
async def reports_menu(callback: types.CallbackQuery, tg_id: str) -> None:
    """Меню отчетов для администратора"""
    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t("select_report_type", lang)
    keyboard = await kb.reports_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "admin-reports")
async def choose_period(callback: types.CallbackQuery, tg_id: str) -> None:
    """Вспомогательная функция для выбора периода для всех отчетов"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]

    text = await t.t("select_period", lang)
    keyboard = await kb.select_period_keyboard(report_type, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Индивидуальный отчет по механику
@router.callback_query(F.data.slpit("|")[0] == "reports-period" and F.data.split("|")[1] == "individual_mechanic_report")
async def choose_mechanic(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Выбор механика для отчета"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    text = await t.t("select_mechanic", lang)

    mechanics = await AsyncOrm.get_all_mechanics(session)
    keyboard = await kb.choose_mechanic(mechanics, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.slpit("|")[0] == "mechanic")
async def mechanic_report(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Отчет по механику за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    user_id = int(callback.data.split("|")[2])

    waiting_message = await callback.message.edit_text(await t.t("please_wait"), lang)

    # mechanic
    user = await AsyncOrm.get_user_by_id(user_id, session)
    text = user.username + "\n\n"

    # количество работ
    operations = await AsyncOrm.get_operations_for_user_by_period(user.tg_id, period, session)
    operations_count = len(operations)
    text += await t.t("number_of_works", lang) + " " + operations_count

    # количество потраченного времени
    duration_sum = sum([operation.duration for operation in operations])


