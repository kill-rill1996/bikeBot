import datetime
from typing import Any

from routers.menu import show_main_menu
from schemas.operations import Operation, OperationAdd
from settings import settings

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from utils.translator import translator as t
from utils.date_time_service import get_dates_by_period
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


@router.callback_query(F.data.split("|")[0] == "mechanic")
async def mechanic_report(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Отчет по механику за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    user_id = int(callback.data.split("|")[2])

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    user = await AsyncOrm.get_user_by_id(user_id, session)

    start_date, end_date = get_dates_by_period(period)
    operations = await AsyncOrm.get_operations_for_user_by_period(user.tg_id, start_date, end_date, session)

    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to_mechanic(period, "individual_mechanic_report",  lang)
        await callback.message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    # mechanic
    text = f"📆 {await t.t('individual_mechanic_report', lang)}\n{user.username}\n\n"

    # количество работ
    jobs_count = sum([len(operation.jobs) for operation in operations])
    text += await t.t("number_of_works", lang) + " " + f"<b>{str(jobs_count)}</b>" + "\n"

    # количество потраченного времени
    duration_sum = str(sum([operation.duration for operation in operations]))
    text += await t.t("total_time_spent", lang) + " " + f"<b>{duration_sum}</b>" + " " + await t.t("minutes", lang) + "\n\n"

    # Список всех работ с деталями
    text += await t.t("work_list", lang) + "\n"
    for idx, operation in enumerate(operations, start=1):
        row_text = f"<b>{idx})</b> {convert_date_time(operation.created_at)[0]} | {str(operation.duration)} {await t.t('minutes', lang)} | " \
                   f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}-{operation.transport_serial_number}\n"

        # jobs для каждой операции
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        # комментарий
        row_text += f'{await t.t("comment", lang)} <i>"{operation.comment}"</i>\n'

        # среднее время на одну работу
        row_text += await t.t("avg_time", lang) + " " + f"{round(int(duration_sum) / jobs_count)} " + await t.t("minutes", lang)

        text += row_text + "\n\n"

    keyboard = await kb.report_details_keyboard(period, "individual_mechanic_report",  lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Сводный отчет по механикам
@router.callback_query(F.data.slpit("|")[0] == "reports-period" and F.data.split("|")[1] == "summary_report_by_mechanics")
async def summary_report_by_mechanic(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Сводный отчет по механикам"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    start_date, end_date = get_dates_by_period(period)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    mechanics = await AsyncOrm.get_all_mechanics(session)

    text = f"📆 {await t.t('summary_report_by_mechanics', lang)}\n\n"

    works_count_rating = {}

    for idx, mechanic in enumerate(mechanics, start=1):
        operations = await AsyncOrm.get_operations_for_user_by_period(mechanic.tg_id, start_date, end_date, session)

        # количество работ
        jobs_count = sum([len(operation.jobs) for operation in operations])
        row_text = f"<b>{idx}) {mechanic.username}</b>\n{await t.t('works_count', lang)} {str(jobs_count)}"

        # общее и среднее время
        duration_sum = sum([operation.duration for operation in operations])
        if jobs_count != 0:
            avg_time = round(int(duration_sum) / jobs_count)
        else:
            avg_time = 0
        row_text += f"{await t.t('works_time', lang)} {duration_sum}\n"
        row_text += f"{await t.t('avg_works', lang)} {avg_time}"

        # запись для рейтинга
        works_count_rating[mechanic.username] = jobs_count

        text += row_text + "\n\n"

    # рейтинг механиков
    text += f"<b>{await t.t('rating_works', lang)}</b>\n"
    sorted_mechanics = {k: v for k, v in sorted(works_count_rating.items(), key=lambda item: item[1], reverse=True)}
    for k, v in sorted_mechanics.items():
        text += f"{k} {v}\n"

    keyboard = await kb.summary_report_details_keyboard(report_type, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Отчет по транспорту
@router.callback_query(F.data.slpit("|")[0] == "reports-period" and F.data.split("|")[1] == "vehicle_report")
async def vehicle_report_select_type(callback: types.CallbackQuery, tg_id: str) -> None:
    """Выбор типа отчета по транспорту"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    text = await t.t("choose_vehicle_report_type", lang)
    keyboard = await kb.select_vehicle_report_type(report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.slpit("|")[0] == "vehicle_report_type" and F.data.split("|")[1] == "by_subcategory")
async def vehicle_report_by_category(callback: types.CallbackQuery, tg_id: str) -> None:
    """Выбор подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]

    text = await t.t("choose_subcategory", lang)
    keyboard = await kb.select_vehicle_subcategory(report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())








