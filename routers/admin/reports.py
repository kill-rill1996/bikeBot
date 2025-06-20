import datetime
import os
from typing import Any

from aiogram import Router, F, types
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from cache import r
from logger import logger
from routers.states.reports import IndividualMechanicReport, SummaryMechanicReport, TransportReport, JobTypesReport, \
    InefficiencyReport, LocationReport
from schemas.categories_and_jobs import Jobtype, Category
from schemas.location import Location
from schemas.reports import OperationWithJobs, JobForJobtypes
from schemas.users import User
from utils.excel_reports import individual_mechanic_excel_report, summary_mechanics_excel_report, \
    vehicle_report_by_transport_excel_report, vehicle_report_by_subcategory_excel_report, \
    vehicle_report_by_category_excel_report, categories_work_excel_report, locations_excel_report, \
    inefficiency_excel_report
from utils.graphics import mechanic_report_graphic, all_mechanics_report_graphic, location_graphic_report, \
    transport_by_category_graphic_report, transport_by_subcategory_graphic_report, \
    transport_by_transport_graphic_report, jobtypes_for_category_graphic, inefficiency_graphic
from utils.translator import translator as t
from utils.date_time_service import get_dates_by_period, get_next_and_prev_month_and_year, convert_str_to_datetime
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
async def choose_period(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Вспомогательная функция для выбора периода для всех отчетов"""
    try:
        await state.clear()
    except Exception as e:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]

    # устанавливаем стейт для каждого отчета отдельно
    if report_type == "individual_mechanic_report":
        await state.set_state(IndividualMechanicReport.period)
    elif report_type == "summary_report_by_mechanics":
        await state.set_state(SummaryMechanicReport.period)
    elif report_type == "vehicle_report":
        await state.set_state(TransportReport.period)
    elif report_type == "work_categories_report":
        await state.set_state(JobTypesReport.period)
    elif report_type == "inefficiency_report":
        await state.set_state(InefficiencyReport.period)
    elif report_type == "location_report":
        await state.set_state(LocationReport.period)

    # записываем тип отчета в стейт
    await state.update_data(report_type=report_type)

    text = await t.t("select_period", lang)
    keyboard = await kb.select_period_keyboard(report_type, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[2] == "custom"))
@router.callback_query(F.data.split("|")[0] == "select_end_date")
@router.callback_query(F.data.split("|")[0] == "action")
async def custom_period_choose(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Вспомогательная функция для выбора кастомного периода"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]

    # для выбора второй даты
    if callback.data.split("|")[0] == "select_end_date":

        # устанавливаем стейт для каждого отчета отдельно
        if report_type == "individual_mechanic_report":
            await state.set_state(IndividualMechanicReport.end_date)
        elif report_type == "summary_report_by_mechanics":
            await state.set_state(SummaryMechanicReport.report)
        elif report_type == "vehicle_report":
            await state.set_state(TransportReport.report)
        elif report_type == "work_categories_report":
            await state.set_state(JobTypesReport.report)
        elif report_type == "inefficiency_report":
            await state.set_state(InefficiencyReport.report)
        elif report_type == "location_report":
            await state.set_state(LocationReport.report)

        # собираем первую дату
        start_date_str = callback.data.split("|")[2]
        start_date = convert_str_to_datetime(start_date_str)

        # записываем первую дату в стейт
        await state.update_data(start_date=start_date)

        # данные для формирования клавиатуры
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month
        dates_data = get_next_and_prev_month_and_year(now_month, now_year)

        text = await t.t("select_date_end", lang) + f"\n{convert_date_time(start_date, with_tz=True)[0]}-"
        keyboard = await kb.select_custom_date(report_type, now_year, now_month, lang, dates_data=dates_data, end_date=True)

    # для выбора первой даты
    elif callback.data.split("|")[0] == "reports-period" and callback.data.split("|")[2] == "custom":
        # данные для формирования клавиатуры
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month
        dates_data = get_next_and_prev_month_and_year(now_month, now_year)

        text = await t.t("select_date_start", lang)
        keyboard = await kb.select_custom_date(report_type, now_year, now_month, lang, dates_data=dates_data)

    # для перелистывания месяцев
    else:
        month = int(callback.data.split("|")[2])
        year = int(callback.data.split("|")[3])

        # для перелистывания в первом и втором выборе
        data = await state.get_data()
        if data.get("start_date"):
            end_date = True
            start_date = convert_date_time(data["start_date"], with_tz=True)[0]
            text = await t.t("select_date_end", lang) + f"\n{start_date}-"
        else:
            end_date = False
            text = await t.t("select_date_start", lang)

        # данные для формирования клавиатуры
        dates_data = get_next_and_prev_month_and_year(month, year)

        keyboard = await kb.select_custom_date(report_type, year, month, lang, dates_data=dates_data, end_date=end_date)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Индивидуальный отчет по механику
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "individual_mechanic_report"))
@router.callback_query(F.data.split("|")[0] == "clndr", IndividualMechanicReport.end_date)
async def choose_mechanic(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор механика для отчета"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        # записываем обе даты в стейт
        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)

    # меняем стейт
    await state.set_state(IndividualMechanicReport.report)

    text = await t.t("select_mechanic", lang)

    mechanics = await AsyncOrm.get_all_mechanics(session)
    keyboard = await kb.choose_mechanic(mechanics, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "mechanic", IndividualMechanicReport.report)
async def mechanic_report(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по механику за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    user_id = int(callback.data.split("|")[2])

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    user = await AsyncOrm.get_user_by_id(user_id, session)

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)

        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)
    else:
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = data["end_date"]

    # получаем операции для периода
    operations = await AsyncOrm.get_operations_for_user_by_period(user.tg_id, start_date, end_date, session)

    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to_mechanic(period, "individual_mechanic_report",  lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    # mechanic
    text = f"📆 {await t.t('individual_mechanic_report', lang)}\n{user.username}\n\n"

    jobs_count = sum([len(operation.jobs) for operation in operations])
    duration_sum = str(sum([operation.duration for operation in operations]))
    avg_time = round(int(duration_sum) / jobs_count)

    # количество работ
    text += await t.t("number_of_works", lang) + " " + f"<b>{str(jobs_count)}</b>" + "\n"

    # среднее время на работу
    text += await t.t("excel_avg_time", lang) + " " + f"<b>{avg_time}</b>" + " " + await t.t("minutes", lang) + "\n"

    # количество потраченного времени
    text += await t.t("total_time_spent", lang) + " " + f"<b>{duration_sum}</b>" + " " + await t.t("minutes", lang) + "\n\n"

    # Список всех работ с деталями
    text += await t.t("work_list", lang) + "\n"
    for idx, operation in enumerate(operations[:15], start=1):
        date, time = convert_date_time(operation.created_at, with_tz=True)
        row_text = f"<b>{idx})</b> ID {operation.id} | {date} {time} | {str(operation.duration)} {await t.t('minutes', lang)} | " \
                   f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}-{operation.transport_serial_number}\n"

        # группа узлов
        row_text += await t.t(operation.jobs[0].jobtype_title, lang) + ":\n"

        # jobs для каждой операции
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        # местоположение
        location = await AsyncOrm.get_location_by_id(operation.location_id, session)
        row_text += f"{await t.t('location', lang)}: {await t.t(location.name, lang)}\n"

        # комментарий
        comment = operation.comment if operation.comment else "-"
        row_text += f'{await t.t("comment", lang)} <i>"{comment}"</i>\n'

        # среднее время на одну работу
        row_text += await t.t("avg_time", lang) + " " + f"{round(operation.duration / len(operation.jobs))} " + await t.t("minutes", lang)

        text += row_text + "\n\n"

    keyboard = await kb.mechanic_report_details_keyboard(period, "individual_mechanic_report", user_id, lang)
    prev_message = await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


# 📆 Сводный отчет по механикам
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "summary_report_by_mechanics"))
@router.callback_query(F.data.split("|")[0] == "clndr", SummaryMechanicReport.report)
async def summary_report_by_mechanics(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Сводный отчет по механикам"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    mechanics = await AsyncOrm.get_all_mechanics(session)

    text = f"📆 {await t.t('summary_report_by_mechanics', lang)}\n\n"

    works_count_rating = {}

    for idx, mechanic in enumerate(mechanics, start=1):
        operations = await AsyncOrm.get_operations_for_user_by_period(mechanic.tg_id, start_date, end_date, session)

        # количество работ
        jobs_count = sum([len(operation.jobs) for operation in operations])
        row_text = f"<b>{idx}) {mechanic.username}</b>\n{await t.t('works_count', lang)} {str(jobs_count)}\n"

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

    keyboard = await kb.summary_report_details_keyboard(report_type, period, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Отчет по транспорту
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "vehicle_report"))
@router.callback_query(F.data.split("|")[0] == "clndr", TransportReport.report)
async def vehicle_report_select_type(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Выбор типа отчета по транспорту"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    text = await t.t("choose_vehicle_report_type", lang)
    keyboard = await kb.select_vehicle_report_type(report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# BY CATEGORY
@router.callback_query(and_f(F.data.split("|")[0] == "vehicle_report_type", F.data.split("|")[1] == "by_category"))
async def vehicle_report_by_category_choose_category(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]
    report_subtype = callback.data.split("|")[1]

    await state.update_data(report_subtype=report_subtype)

    text = await t.t("select_category", lang)
    categories = await AsyncOrm.get_all_categories(session)
    keyboard = await kb.select_vehicle_category(categories, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_report_by_c")
async def vehicle_report_by_category(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по транспорту по категории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    category_id = int(callback.data.split("|")[3])

    await state.update_data(category_id=category_id)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = data["end_date"]

    # получаем операции по датам
    operations = await AsyncOrm.get_operations_by_category_and_period(category_id, start_date, end_date, session)

    # если нет операций
    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to("by_category", period, report_type, lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    # header
    category_title = operations[0].transport_category
    text = f"📆 {await t.t('vehicle_report', lang)}\n{await t.t('category', lang)} <b>{await t.t(category_title, lang)}</b>\n\n"

    # operations
    for idx, operation in enumerate(operations[:15], start=1):
        mechanic = await AsyncOrm.get_user_by_tg_id(operation.tg_id, session)
        location = await AsyncOrm.get_location_by_id(operation.location_id, session)
        date, time = convert_date_time(operation.created_at, with_tz=True)
        row_text = f"<b>{idx})</b> ID {operation.id} | {date} {time} | " \
                   f"{operation.transport_subcategory}-{operation.transport_serial_number} | " \
                   f"{mechanic.username} | {await t.t(location.name, lang)}\n"
        # суммарное время обслуживания
        row_text += f"{await t.t('works_time', lang)} {operation.duration} {await t.t('minutes', lang)}\n"
        comment = operation.comment if operation.comment else "-"
        row_text += f"{await t.t('comment', lang)} <i>'{comment}'</i>\n"

        # jobs
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        text += row_text + "\n"

    back_to = f"vehicle_report_type|by_category|{report_type}|{period}"
    keyboard = await kb.vehicle_report_details_keyboard(back_to, period, report_type, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# BY SUBCATEGORY
@router.callback_query(and_f(F.data.split("|")[0] == "vehicle_report_type", F.data.split("|")[1] == "by_subcategory"))
async def vehicle_report_by_subcategory_choose_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]
    report_subtype = callback.data.split("|")[1]

    await state.update_data(report_subtype=report_subtype)

    text = await t.t("choose_subcategory", lang)
    subcategories = await AsyncOrm.get_all_subcategories(session)
    keyboard = await kb.select_vehicle_subcategory(subcategories, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_report_by_sc")
async def vehicle_report_by_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по транспорту по подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    subcategory_id = int(callback.data.split("|")[3])

    await state.update_data(subcategory_id=subcategory_id)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = data["end_date"]

    # получаем операции
    operations = await AsyncOrm.get_operations_by_subcategory_and_period(subcategory_id, start_date, end_date, session)

    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to("by_subcategory", period, report_type, lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    subcategory = await AsyncOrm.get_subcategory_by_id(subcategory_id, session)
    text = f"📆 {await t.t('vehicle_report', lang)}\n{await t.t('subcategory', lang)} <b>{subcategory.title}</b>\n\n"

    # operations
    for idx, operation in enumerate(operations[:15], start=1):
        mechanic = await AsyncOrm.get_user_by_tg_id(operation.tg_id, session)
        location = await AsyncOrm.get_location_by_id(operation.location_id, session)
        date, time = convert_date_time(operation.created_at, with_tz=True)
        row_text = f"<b>{idx})</b> ID {operation.id} | {date} {time} | " \
                   f"{operation.transport_subcategory}-{operation.transport_serial_number} | " \
                   f"{mechanic.username} | {await t.t(location.name, lang)}\n"
        # суммарное время обслуживания
        row_text += f"{await t.t('works_time', lang)} {operation.duration} {await t.t('minutes', lang)}\n"
        comment = operation.comment if operation.comment else "-"
        row_text += f"{await t.t('comment', lang)} <i>'{comment}'</i>\n"

        # jobs
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        text += row_text + "\n"

    back_to = f"vehicle_report_type|by_subcategory|{report_type}|{period}"
    keyboard = await kb.vehicle_report_details_keyboard(back_to, period, report_type, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# BY TRANSPORT
@router.callback_query(and_f(F.data.split("|")[0] == "vehicle_report_type", F.data.split("|")[1] == "by_transport"))
async def vehicle_report_by_transport_choose_category(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор категории для отчета по серийному номеру транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]
    report_subtype = callback.data.split("|")[1]

    await state.update_data(report_subtype=report_subtype)

    categories = await AsyncOrm.get_all_categories(session)

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category_for_transport_report(categories, report_type, period, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "transport_report_category")
async def vehicle_report_by_transport_choose_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор подкатегории для отчета по серийному номеру транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    category_id = int(callback.data.split("|")[3])

    await state.update_data(category_id=category_id)

    subcategories = await AsyncOrm.get_subcategories_by_category(category_id, session)

    text = await t.t("choose_subcategory", lang)
    keyboard = await kb.select_subcategory_for_transport_report(subcategories, report_type, period, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "transport_report_subcategory")
async def vehicle_report_by_transport_choose_transport(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    subcategory_id = int(callback.data.split("|")[3])

    await state.update_data(subcategory_id=subcategory_id)

    text = await t.t("choose_transport", lang)
    transports = await AsyncOrm.get_transports_for_subcategory(subcategory_id, session)

    await state.update_data(transports=transports)

    page = 1
    keyboard = await kb.transport_pagination_keyboard(transports, page, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(or_f(F.data.split("|")[0] == "prev", F.data.split("|")[0] == "next"))
async def transport_pagination_handler(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Вспомогательный хэндлер для пагинации"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]

    action = callback.data.split("|")[0]
    current_page = int(callback.data.split("|")[1])

    # меняем номер страницы
    if action == "prev":
        page = current_page - 1
    else:
        page = current_page + 1

    # плучаем данные для пагинации
    data = await state.get_data()
    transports = data["transports"]

    keyboard = await kb.transport_pagination_keyboard(transports, page, report_type, period, lang)
    text = await t.t("choose_transport", lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_report_by_t")
async def vehicle_report_by_transport(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по транспорту"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    transport_id = int(callback.data.split("|")[3])

    await state.update_data(transport_id=transport_id)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = data["end_date"]

    operations = await AsyncOrm.get_operations_by_transport_and_period(transport_id, start_date, end_date, session)

    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to("by_transport", period, report_type, lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    transport = await AsyncOrm.get_transport_by_id(transport_id, session)
    text = f"📆 {await t.t('vehicle_report', lang)}\n<b>{transport.subcategory_title}-{transport.serial_number}</b>\n\n"

    # operations
    for idx, operation in enumerate(operations[:15], start=1):
        mechanic = await AsyncOrm.get_user_by_tg_id(operation.tg_id, session)
        location = await AsyncOrm.get_location_by_id(operation.location_id, session)
        date, time = convert_date_time(operation.created_at, with_tz=True)
        row_text = f"<b>{idx})</b> ID {operation.id} | {date} {time} | {mechanic.username} | {await t.t(location.name, lang)}\n"
        # суммарное время обслуживания
        row_text += f"{await t.t('works_time', lang)} {operation.duration} {await t.t('minutes', lang)}\n"
        comment = operation.comment if operation.comment else "-"
        row_text += f"{await t.t('comment', lang)} <i>'{comment}'</i>\n"

        # jobs
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        text += row_text + "\n"

    back_to = f"transport_report_subcategory|{report_type}|{period}|{transport.subcategory_id}"
    keyboard = await kb.vehicle_report_details_keyboard(back_to, period, report_type, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Отчет по категориям работ
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "work_categories_report"))
@router.callback_query(F.data.split("|")[0] == "clndr", JobTypesReport.report)
async def report_by_jobtypes_select_category(callback: types.CallbackQuery, tg_id: int, session: Any, state: FSMContext) -> None:
    """Выбор категории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    text = await t.t("select_category", lang)
    categories = await AsyncOrm.get_all_categories(session)

    keyboard = await kb.select_category_for_jobtypes_report(categories, report_type, period, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "jobtypes_report_category")
@router.callback_query(F.data.split("|")[0] == "back_to_select")
async def report_by_jobtypes_select_jobtypes(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Выбор jobtypes для отчета по работам"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    category_id = int(callback.data.split("|")[3])

    # устанавливаем правильный стейт для мультивыбора (если его нет из кастомного периода)
    await state.set_state(JobTypesReport.report)
    await state.update_data(selected_jobtypes=[])

    # для производительности храним в стейте
    jobtypes = await AsyncOrm.get_job_types_by_category(category_id, session)
    await state.update_data(category_id=category_id)    # TODO ADDED 17.06
    await state.update_data(jobtypes=jobtypes)

    text = await t.t("choose_jobtypes", lang)
    keyboard = await kb.select_jobtypes(jobtypes, [], report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "jobtypes_select", JobTypesReport.report)
async def multiselect(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Вспомогательная функция для мультиселекта"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]
    jobtype_id = int(callback.data.split("|")[1])

    # запись или удаление из стейта выбранного jobtype
    data = await state.get_data()
    selected_jobtypes = data["selected_jobtypes"]
    # удаляем если уже есть
    if jobtype_id in selected_jobtypes:
        selected_jobtypes.remove(jobtype_id)
    # записываем если еще нет
    else:
        selected_jobtypes.append(jobtype_id)
    await state.update_data(selected_jobtypes=selected_jobtypes)

    text = await t.t("choose_jobtypes", lang)
    jobtypes = data["jobtypes"]
    keyboard = await kb.select_jobtypes(jobtypes, selected_jobtypes, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "jobtype_select_done", JobTypesReport.report)
async def report_by_jobtypes(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Отчет по jobtypes"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    data = await state.get_data()
    selected_jobtypes = data["selected_jobtypes"]

    jobtypes = await AsyncOrm.get_jobtypes_by_ids(selected_jobtypes, session)

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    text = f"📆 {await t.t('work_categories_report', lang)}\n\n"

    for idx, jt in enumerate(jobtypes, start=1):
        emoji = jt.emoji + " " if jt.emoji else ""
        row_text = f"<b>{idx})</b> {emoji}{await t.t(jt.title, lang)}\n"

        # количество выполненных операций по категории
        jobs = await AsyncOrm.get_jobs_by_jobtype_with_operation(jt.id, start_date, end_date, session)

        # если работ нет
        if len(jobs) == 0:
            row_text += await t.t("no_works", lang) + "\n\n"
            text += row_text
            continue

        jobs_count = {}
        transport_count = {}
        mechanic_count = {}
        for job in jobs:
            if jobs_count.get(job.job_title):
                jobs_count[job.job_title] += 1
            else:
                jobs_count[job.job_title] = 1

            transport = f"{job.subcategory_title}-{job.serial_number}"
            if transport_count.get(transport):
                transport_count[transport] += 1
            else:
                transport_count[transport] = 1

            if mechanic_count.get(job.mechanic_username):
                mechanic_count[job.mechanic_username] += 1
            else:
                mechanic_count[job.mechanic_username] = 1

        # сортировка работ по количеству
        sorted_jobs = {k: v for k, v in sorted(jobs_count.items(), key=lambda item: item[1], reverse=True)}
        sorted_transport = {k: v for k, v in sorted(transport_count.items(), key=lambda item: item[1], reverse=True)}
        sorted_mechanics = {k: v for k, v in sorted(mechanic_count.items(), key=lambda item: item[1], reverse=True)}

        for k, v in sorted_jobs.items():
            row_text += f"{await t.t(k, lang)}: {v}\n"

        # самые частый транспорт
        row_text += await t.t('most_recent_transport', lang) + "\n"
        counter = 0
        for k, v in sorted_transport.items():
            if counter == 3:
                break
            row_text += f"{k}: {v} "
            counter += 1

        row_text += "\n"

        # самые частые механики в категории
        row_text += await t.t('most_recent_mechanics', lang) + "\n"
        counter = 0
        for k, v in sorted_mechanics.items():
            if counter == 3:
                break
            counter += 1
            row_text += f"{k}: {v} "

        text += row_text + "\n\n"

    keyboard = await kb.jobtypes_report_details_keyboard(report_type, period, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Отчет по неэффективности
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "inefficiency_report"))
@router.callback_query(F.data.split("|")[0] == "clndr", InefficiencyReport.report)
async def inefficiency_report(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по неэффективности"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    operations = await AsyncOrm.get_operations_with_jobs_and_transport_by_period(start_date, end_date, session)

    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to_choose_period(report_type, lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    text = f"📆 {await t.t('inefficiency_report', lang)}\n\n"

    transport_jobs_count = {}
    for o in operations:
        for job in o.jobs:
            key = f"{o.transport_subcategory}-{o.transport_serial_number} {await t.t(job.title, lang)}"

            if transport_jobs_count.get(key):
                transport_jobs_count[key] += 1
            else:
                transport_jobs_count[key] = 1

    # сортируем по количеству
    sorted_jobs = {k: v for k, v in sorted(transport_jobs_count.items(), key=lambda item: item[1], reverse=True)}

    # учитываем работы повторяющиеся только больше определенного количества раз за период
    if period == "today" or period == "yesterday":
        frequent_works = 2
    elif period == "week":
        frequent_works = 7
    elif period == "month":
        frequent_works = 15
    else:
        frequent_works = (end_date - start_date).days

    row_text = ""
    for k, v in sorted_jobs.items():
        if v >= frequent_works:
            row_text += "\t\t• " + k + f": {v}" + "\n"

    # повторяющиеся работы за период
    if row_text:
        text += await t.t("repeatable_jobs", lang) + "\n"
        text += row_text + "\n"

    # операции без комментариев
    text += await t.t("no_comments", lang) + "\n"
    for o in operations:
        if not o.comment:
            date, time = convert_date_time(o.created_at, with_tz=True)
            row_text = f"{date} {time} | ID {o.id} | " \
                       f"{o.transport_subcategory}-{o.transport_serial_number}\n"
            text += row_text

    keyboard = await kb.efficient_report_details_keyboard(report_type, period, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Отчет по местоположению
@router.callback_query(and_f(F.data.split("|")[0] == "reports-period", F.data.split("|")[1] == "location_report"))
@router.callback_query(F.data.split("|")[0] == "clndr", LocationReport.report)
async def location_report_select_location(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выбор локации для отчета"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    text = await t.t("choose_location", lang)

    locations = await AsyncOrm.get_locations(session)
    keyboard = await kb.select_location(locations, report_type, period, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "select_location")
async def location_report(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отчет по местоположению"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    location_id = int(callback.data.split("|")[3])

    await state.update_data(location_id=location_id)

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = data["end_date"]

    # получаем операции по датам
    location = await AsyncOrm.get_location_by_id(location_id, session)
    operations = await AsyncOrm.get_operations_by_location_and_period(location_id, start_date, end_date, session)

    # если нет операций
    if not operations:
        msg_text = await t.t("no_operations", lang)
        keyboard = await kb.back_to_location(period, report_type, lang)
        await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
        return

    # header
    text = f"📆 {await t.t('location_report', lang)}\n{await t.t(location.name, lang)}\n\n"

    # operations
    unique_transport = {}
    current_category = operations[0].transport_category
    current_subcategory = operations[0].transport_subcategory
    category_counter = 0
    subcategory_counter = 0
    total_counter = 0
    text += f"{await t.t(operations[0].transport_category, lang)}\n" \
            f"{await t.t('subcategory', lang)} {operations[0].transport_subcategory}\n\n"

    for idx, operation in enumerate(operations, start=1):
        if unique_transport.get(f"{operation.transport_subcategory}-{operation.transport_serial_number}"):
            continue
        else:
            # чтобы не повторялся транспорт из операций
            key = f"{operation.transport_subcategory}-{operation.transport_serial_number}"
            unique_transport[key] = True

            # смена подкатегории для разбивки
            if operation.transport_subcategory != current_subcategory:
                # смена категории для разбивки
                if operation.transport_category != current_category:
                    # записываем итоги категории и подкатегории
                    text += f'{await t.t("total", lang)} {current_subcategory}: {subcategory_counter} {await t.t("items", lang)}\n'
                    text += f'{await t.t("total", lang)} {await t.t(current_category, lang)}: {category_counter} {await t.t("items", lang)}\n\n'

                    # записываем заголовки новых категории и подкатегории
                    text += f"{await t.t(operation.transport_category, lang)}\n" \
                            f"{await t.t('subcategory', lang)} {operation.transport_subcategory}\n\n"

                    # меняем текущие подкатегорию и категорию
                    current_category = operation.transport_category
                    current_subcategory = operation.transport_subcategory
                    category_counter = 0
                    subcategory_counter = 0

                # без смены категории
                else:
                    # записываем итоги подкатегории
                    text += f'{await t.t("total", lang)} {current_subcategory}: {subcategory_counter} {await t.t("items", lang)}\n\n'

                    # записываем заголовок новой подкатегории
                    text += f"{await t.t('subcategory', lang)} {operation.transport_subcategory}\n\n"

                    # меняем текущие подкатегорию
                    current_subcategory = operation.transport_subcategory
                    subcategory_counter = 0

            date, time = convert_date_time(operation.created_at, with_tz=True)
            row_text = f"{operation.transport_subcategory}-{operation.transport_serial_number} \t\t {date} {time}\n"
            text += row_text
            category_counter += 1
            subcategory_counter += 1
            total_counter += 1

    # запись последних строк
    text += f'{await t.t("total", lang)} {current_subcategory}: {subcategory_counter} {await t.t("items", lang)}\n'
    text += f'{await t.t("total", lang)} {await t.t(current_category, lang)}: {category_counter} {await t.t("items", lang)}\n\n'

    # запись финального подсчета на складе
    text += f'{await t.t("total_on_warehouse", lang)}: {total_counter} {await t.t("items", lang)}\n\n'

    # ограничение по количеству
    if len(text) > 4000:
        text = text[:4000]

    keyboard = await kb.location_report_details_keyboard(report_type, period, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "excel_export")
async def send_excel_file(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отправка эксель файла для типа отчета"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]
    data = await state.get_data()

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    # скидываем стейт
    # try:
    #     await state.clear()
    # except Exception:
    #     pass

    # 📆 Индивидуальный отчет по механику
    if report_type == "individual_mechanic_report":
        # получаем данные для отчета
        user_id = int(callback.data.split("|")[3])
        user = await AsyncOrm.get_user_by_id(user_id, session)
        operations = await AsyncOrm.get_operations_for_user_by_period(user.tg_id, start_date, end_date, session)

        # путь до отчета
        file_path = await individual_mechanic_excel_report(operations, user.username, start_date, end_date, report_type, lang, session)
        document = FSInputFile(file_path)

        # текст сообщения
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('individual_mechanic_report', lang)} {start_date_formatted} - {end_date_formatted}"

        # формируем callback для кнопки назад
        back_callback = f"mechanic|{period}|{user_id}"

    # 📆 Сводный отчет по механикам
    elif report_type == "summary_report_by_mechanics":
        # путь до отчета
        file_path = await summary_mechanics_excel_report(start_date, end_date, report_type, lang, session)
        document = FSInputFile(file_path)

        # текст сообщения
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('summary_report_by_mechanics', lang)} {start_date_formatted} - {end_date_formatted}"

        # формируем callback для кнопки назад
        if period != "custom":
            back_callback = f"reports-period|summary_report_by_mechanics|{period}"
        else:
            back_callback = f"clndr|summary_report_by_mechanics|{period}|{end_date_formatted}"

    # 📆 Отчет по транспорту
    elif report_type == "vehicle_report":
        report_subtype = data["report_subtype"]

        if report_subtype == "by_category":
            # данные для отчета
            category_id = data["category_id"]
            operations = await AsyncOrm.get_operations_by_category_and_period(category_id, start_date, end_date, session)
            category_title = operations[0].transport_category

            # путь до отчета
            file_path = await vehicle_report_by_category_excel_report(operations, start_date, end_date, report_type,
                                                                         report_subtype, lang, session,
                                                                         category_title=category_title)
            document = FSInputFile(file_path)

            # текст сообщения
            start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
            end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
            text = f"{await t.t('vehicle_report', lang)} {start_date_formatted} - {end_date_formatted}"

            # формируем callback для кнопки назад
            back_callback = f"vehicle_report_by_c|{report_type}|{period}|{category_id}"

        elif report_subtype == "by_subcategory":
            # данные для отчета
            subcategory_id = data["subcategory_id"]
            subcategory = await AsyncOrm.get_subcategory_by_id(subcategory_id, session)
            operations = await AsyncOrm.get_operations_by_subcategory_and_period(subcategory_id, start_date, end_date, session)

            # путь до отчета
            file_path = await vehicle_report_by_subcategory_excel_report(operations, start_date, end_date, report_type,
                                                                       report_subtype, lang, session, subcategory=subcategory)
            document = FSInputFile(file_path)

            # текст сообщения
            start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
            end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
            text = f"{await t.t('vehicle_report', lang)} {start_date_formatted} - {end_date_formatted}"

            # формируем callback для кнопки назад
            back_callback = f"vehicle_report_by_sc|{report_type}|{period}|{subcategory_id}"

        else:
            # данные для отчета
            transport_id = data["transport_id"]
            operations = await AsyncOrm.get_operations_by_transport_and_period(transport_id, start_date, end_date, session)
            transport = await AsyncOrm.get_transport_by_id(transport_id, session)

            # путь до отчета
            file_path = await vehicle_report_by_transport_excel_report(operations, start_date, end_date, report_type,
                                                                       report_subtype, lang, session, transport=transport)
            document = FSInputFile(file_path)

            # текст сообщения
            start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
            end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
            text = f"{await t.t('vehicle_report', lang)} {start_date_formatted} - {end_date_formatted}"

            # формируем callback для кнопки назад
            back_callback = f"vehicle_report_by_t|{report_type}|{period}|{transport_id}"

    # 📆 Отчет по категориям работ
    elif report_type == "work_categories_report":
        # данные для отчета
        selected_jobtypes = data["selected_jobtypes"]
        jobtypes = await AsyncOrm.get_jobtypes_by_ids(selected_jobtypes, session)

        # путь до отчета
        file_path = await categories_work_excel_report(jobtypes, start_date, end_date, report_type, lang, session)
        document = FSInputFile(file_path)

        # текст сообщения
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('work_categories_report', lang)} {start_date_formatted} - {end_date_formatted}"

        # формируем callback для кнопки назад
        back_callback = f"jobtype_select_done|{report_type}|{period}"

    # 📆 Отчет по неэффективности
    elif report_type == "inefficiency_report":
        # данные для отчета
        operations = await AsyncOrm.get_operations_with_jobs_and_transport_by_period(start_date, end_date, session)

        # путь до отчета
        file_path = await inefficiency_excel_report(operations, start_date, end_date, report_type, lang, period)
        document = FSInputFile(file_path)

        # текст сообщения
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('inefficiency_report', lang)} {start_date_formatted} - {end_date_formatted}"

        # формируем callback для кнопки назад
        if period != "custom":
            back_callback = f"reports-period|{report_type}|{period}"
        else:
            back_callback = f"clndr|{report_type}|{period}|{end_date_formatted}"

    # 📆 Отчет по местоположению
    elif report_type == "location_report":
        # данные для отчета
        location_id = data["location_id"]
        location = await AsyncOrm.get_location_by_id(location_id, session)
        operations = await AsyncOrm.get_operations_by_location_and_period(location_id, start_date, end_date, session)

        # путь до отчета
        file_path = await locations_excel_report(operations, start_date, end_date, report_type, lang, location)
        document = FSInputFile(file_path)

        # текст сообщения
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('location_report', lang)} {location.name} {start_date_formatted} - {end_date_formatted}"

        # формируем callback для кнопки назад
        back_callback = f"select_location|location_report|{period}|{location_id}"

    # удаляем сообщение для ожидания
    await waiting_message.delete()

    # отправляем отчет
    await callback.message.answer_document(document, caption=text)

    # отправляем сообщение с клавиатурой
    text = await t.t("excel_ready", lang)
    keyboard = await kb.excel_ready_keyboard(back_callback, lang)
    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем отчет
    try:
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Не удалось удалить файл с отчетом {file_path}: {e}")


# GRAPHIC INDIVIDUAL MECHANIC REPORT
@router.callback_query(F.data.split("|")[0] == "graphic-mechanic")
async def individual_mechanic_graphic(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """График по индивидуальным отчетам механиков"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    user_id = int(callback.data.split("|")[2])
    data = await state.get_data()

    # меняем предыдущее сообщение
    try:
        await data["prev_message"].edit_text(callback.message.text)
    except:
        pass

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)

        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    # получаем операции для периода
    mechanic: User = await AsyncOrm.get_user_by_id(user_id, session)
    operations: list[OperationWithJobs] = await AsyncOrm.get_operations_for_user_by_period(mechanic.tg_id, start_date, end_date, session)

    # создаем словарь с кол-вом времени по дням формата {day:(duration, count)...}
    durations_by_dates = {}
    for operation in operations:
        date_str = convert_date_time(operation.created_at, with_tz=True)[0]
        if date_str not in durations_by_dates.keys():
            durations_by_dates[date_str] = (operation.duration, 1)
        else:
            durations_by_dates[date_str] = (durations_by_dates[date_str][0] + operation.duration,  durations_by_dates[date_str][1] + 1)

    # данные для подписи оси Х (выписываем все даты за выбранный период)
    dates_period = []
    current_date = start_date
    while current_date.date() <= end_date.date():
        dates_period.append(current_date)
        current_date += datetime.timedelta(days=1)

    # формируем данные для графика формата [(date, sum_duration, count)...]
    graphic_data: list[tuple] = []
    for day in dates_period:
        str_date = convert_date_time(day)[0]
        if durations_by_dates.get(str_date):
            graphic_data.append((str_date, durations_by_dates[str_date][0], durations_by_dates[str_date][1]))
        else:
            graphic_data.append((str_date, 0, 0))

    x = [item[0][:5] for item in graphic_data]  # даты для значений на оси Х
    y_1 = [item[1] for item in graphic_data]  # Данные о времени работ для оси Y duration
    y_2 = [item[2] for item in graphic_data]   # Данные о времени работ для оси Y operaions count

    # строим график и получаем путь до него
    chart_path = mechanic_report_graphic(durations_by_dates, y_1, y_2, x, mechanic, start_date, end_date)

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(
            photo=FSInputFile(chart_path),
        )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        text = await t.t("graphic_error", lang)

    # отправляем сообщение для дальнейшего выбора
    keyboard = await kb.back_keyboard(f"mechanic|{period}|{user_id}", lang)
    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем график
    try:
        os.remove(chart_path)
    except Exception as e:
        logger.error(f"Ошибка удаления графика {chart_path}: {e}")


# GRAPHIC ALL MECHANICS REPORT
@router.callback_query(F.data.split("|")[0] == "graphic-mechanics")
async def all_mechanics_graphic(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """График по всем механикам"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    data = await state.get_data()

    # меняем предыдущее сообщение
    try:
        await data["prev_message"].edit_text(callback.message.text)
    except:
        pass

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)

        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    mechanics: list[User] = await AsyncOrm.get_all_mechanics(session)

    mechanic_duration_count = {}

    for mechanic in mechanics:
        operations: list[OperationWithJobs] = await AsyncOrm.get_operations_for_user_by_period(
            mechanic.tg_id, start_date, end_date, session)

        # количество работ
        jobs_count = sum([len(operation.jobs) for operation in operations])

        # общее и среднее время
        duration_sum = sum([operation.duration for operation in operations])

        mechanic_duration_count[mechanic.username] = (duration_sum, jobs_count)

    # строим график и получаем путь до него
    chart_path = all_mechanics_report_graphic(mechanic_duration_count, start_date, end_date)

    # Удаляем сообщение об ожидании
    try:
        await waiting_message.delete()
    except:
        pass

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(
            photo=FSInputFile(chart_path),
        )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        text = await t.t("graphic_error", lang)

    # отправляем сообщение для дальнейшего выбора
    if period != "custom":
        keyboard = await kb.back_keyboard(f"reports-period|summary_report_by_mechanics|{period}", lang)
    else:
        end_date_callback = convert_date_time(end_date)[0]
        keyboard = await kb.back_keyboard(f"clndr|summary_report_by_mechanics|{period}|{end_date_callback}", lang)

    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем график
    try:
        os.remove(chart_path)
    except Exception as e:
        logger.error(f"Ошибка удаления графика {chart_path}: {e}")


# GRAPHIC LOCATION REPORT
@router.callback_query(F.data.split("|")[0] == "graphic-location")
async def location_graphic(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """График по всем механикам"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    data = await state.get_data()
    location_id = data["location_id"]

    # меняем предыдущее сообщение
    try:
        await data["prev_message"].edit_text(callback.message.text)
    except:
        pass

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)

        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # Получаем данные из ДБ
    location: Location = await AsyncOrm.get_location_by_id(location_id, session)
    operations: list[OperationWithJobs] = await AsyncOrm.get_operations_by_location_and_period(
                                                        location_id, start_date, end_date, session)

    operations_dict = {}    # {'date_str': {'Velosiped U': 2, 'Samocati E': 1}}
    already_checked_transport = {}
    for operation in operations:
        date_str = convert_date_time(operation.created_at)[0]

        if not already_checked_transport.get(date_str):
            already_checked_transport[date_str] = []

        # проверяем был ли уже этот транспорт учтен
        if f"{operation.transport_subcategory} {operation.transport_subcategory} {operation.transport_serial_number}" in already_checked_transport[date_str]:
            continue

        key = f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}"

        # записываем в словарь по датам и ключу 'Velosipedi U'
        if operations_dict.get(date_str):
            if operations_dict[date_str].get(key):
               operations_dict[date_str][key] += 1
            else:
                operations_dict[date_str][key] = 1
        else:
            operations_dict[date_str] = {key: 1}

        # помечаем что этот траспорт уже учтен
        already_checked_transport[date_str].append(f"{operation.transport_subcategory} {operation.transport_subcategory} {operation.transport_serial_number}")

    # строим график и получаем путь до него
    start_date_str = convert_date_time(start_date)[0]
    end_date_str = convert_date_time(end_date)[0]
    chart_path = location_graphic_report(operations_dict, start_date_str, end_date_str, await t.t(location.name, lang))

    # Удаляем сообщение об ожидании
    try:
        await waiting_message.delete()
    except:
        pass

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(
            photo=FSInputFile(chart_path),
        )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        text = await t.t("graphic_error", lang)

    # отправляем сообщение для дальнейшего выбора
    keyboard = await kb.back_keyboard(f"select_location|location_report|{period}|{location_id}", lang)

    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем график
    try:
        os.remove(chart_path)
    except Exception as e:
        logger.error(f"Ошибка удаления графика {chart_path}: {e}")


# GRAPHIC TRANSPORT REPORT
@router.callback_query(F.data.split("|")[0] == "graphic-transport")
async def transport_by_category_graphic(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """График отчетов по транспорту"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    data = await state.get_data()
    report_subtype = data["report_subtype"]
    report_type = data["report_type"]

    # меняем предыдущее сообщение
    try:
        waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))
    except Exception:
        pass

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)

        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    if report_subtype == "by_category":
        # получаем данные из БД
        category_id = data["category_id"]
        category = await AsyncOrm.get_category_by_id(category_id, session)
        category_title = await t.t(category.title, lang)
        operations: list[OperationWithJobs] = await AsyncOrm.get_operations_by_category_and_period(category_id, start_date, end_date, session)

        # создаем словарь с кол-вом времени по дням формата {day: count,...}
        jobs_count_by_dates = {}
        for operation in operations:
            date_str = convert_date_time(operation.created_at, with_tz=True)[0]
            if date_str not in jobs_count_by_dates.keys():
                jobs_count_by_dates[date_str] = len(operation.jobs)
            else:
                jobs_count_by_dates[date_str] += len(operation.jobs)

        # данные для подписи оси Х (выписываем все даты за выбранный период)
        dates_period = []
        current_date = start_date
        while current_date.date() <= end_date.date():
            dates_period.append(current_date)
            current_date += datetime.timedelta(days=1)

        # формируем данные для графика формата [(date, count)...]
        graphic_data: list[tuple] = []
        for day in dates_period:
            str_date = convert_date_time(day)[0]
            if jobs_count_by_dates.get(str_date):
                graphic_data.append((str_date, jobs_count_by_dates[str_date]))
            else:
                graphic_data.append((str_date, 0))

        x = [item[0][:5] for item in graphic_data]  # даты для значений на оси Х
        y = [item[1] for item in graphic_data]  # Данные о времени работ для оси Y jobs count

        # строим график и получаем путь до него
        chart_path = transport_by_category_graphic_report(jobs_count_by_dates, y, x, category_title, start_date, end_date)

        # колбэк назад
        back_callback = f"vehicle_report_by_c|{report_type}|{period}|{category_id}"

    elif report_subtype == "by_subcategory":
        # получаем данные из БД
        subcategory_id = data["subcategory_id"]
        subcategory = await AsyncOrm.get_subcategory_by_id(subcategory_id, session)
        subcategory_title = subcategory.title
        operations = await AsyncOrm.get_operations_by_subcategory_and_period(subcategory_id, start_date, end_date,
                                                                             session)

        # создаем словарь с кол-вом времени по дням формата {day: count,...}
        jobs_count_by_dates = {}
        for operation in operations:
            date_str = convert_date_time(operation.created_at, with_tz=True)[0]
            if date_str not in jobs_count_by_dates.keys():
                jobs_count_by_dates[date_str] = len(operation.jobs)
            else:
                jobs_count_by_dates[date_str] += len(operation.jobs)

        # данные для подписи оси Х (выписываем все даты за выбранный период)
        dates_period = []
        current_date = start_date
        while current_date.date() <= end_date.date():
            dates_period.append(current_date)
            current_date += datetime.timedelta(days=1)

        # формируем данные для графика формата [(date, count)...]
        graphic_data: list[tuple] = []
        for day in dates_period:
            str_date = convert_date_time(day)[0]
            if jobs_count_by_dates.get(str_date):
                graphic_data.append((str_date, jobs_count_by_dates[str_date]))
            else:
                graphic_data.append((str_date, 0))

        x = [item[0][:5] for item in graphic_data]  # даты для значений на оси Х
        y = [item[1] for item in graphic_data]  # Данные о времени работ для оси Y jobs count

        # строим график и получаем путь до него
        chart_path = transport_by_subcategory_graphic_report(jobs_count_by_dates, y, x, subcategory_title, start_date,
                                                          end_date)

        # колбэк назад
        back_callback = f"vehicle_report_by_sc|{report_type}|{period}|{subcategory_id}"

    elif report_subtype == "by_transport":
        # получаем данные из БД
        transport_id = data["transport_id"]
        transport = await AsyncOrm.get_transport_by_id(transport_id, session)
        transport_title = f"{transport.subcategory_title}-{transport.serial_number}"
        operations = await AsyncOrm.get_operations_by_transport_and_period(transport_id, start_date, end_date, session)

        # создаем словарь с кол-вом времени по дням формата {day: count,...}
        jobs_count_by_dates = {}
        for operation in operations:
            date_str = convert_date_time(operation.created_at, with_tz=True)[0]
            if date_str not in jobs_count_by_dates.keys():
                jobs_count_by_dates[date_str] = len(operation.jobs)
            else:
                jobs_count_by_dates[date_str] += len(operation.jobs)

        # данные для подписи оси Х (выписываем все даты за выбранный период)
        dates_period = []
        current_date = start_date
        while current_date.date() <= end_date.date():
            dates_period.append(current_date)
            current_date += datetime.timedelta(days=1)

        # формируем данные для графика формата [(date, count)...]
        graphic_data: list[tuple] = []
        for day in dates_period:
            str_date = convert_date_time(day)[0]
            if jobs_count_by_dates.get(str_date):
                graphic_data.append((str_date, jobs_count_by_dates[str_date]))
            else:
                graphic_data.append((str_date, 0))

        x = [item[0][:5] for item in graphic_data]  # даты для значений на оси Х
        y = [item[1] for item in graphic_data]  # Данные о времени работ для оси Y jobs count

        # строим график и получаем путь до него
        chart_path = transport_by_transport_graphic_report(jobs_count_by_dates, y, x, transport_title, start_date,
                                                          end_date)

        back_callback = f"vehicle_report_by_t|{report_type}|{period}|{transport_id}"

    # удаляем сообщение об ожидании
    try:
        await waiting_message.delete()
    except Exception:
        pass

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(photo=FSInputFile(chart_path), )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        text = await t.t("graphic_error", lang)

    # отправляем сообщение для дальнейшего выбора
    keyboard = await kb.back_keyboard(back_callback, lang)
    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем график
    try:
        os.remove(chart_path)
    except Exception as e:
        logger.error(f"Ошибка удаления графика {chart_path}: {e}")


# GRAPHIC JOBTYPES REPORT
@router.callback_query(F.data.split("|")[0] == "graphic-jobtypes")
async def jobtypes_graphic(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Отправка графика по подкатегориям узлов"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    data = await state.get_data()

    # меняем предыдущее сообщение
    try:
        await data["prev_message"].edit_text(callback.message.text)
    except:
        pass

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    # Получаем данные из ДБ
    selected_jobtypes = data["selected_jobtypes"]
    category_id = int(data["category_id"])

    jobtypes: list[Jobtype] = await AsyncOrm.get_jobtypes_by_ids(selected_jobtypes, session)
    category: Category = await AsyncOrm.get_category_by_id(category_id, session)

    # данные для подписи оси Х (выписываем все даты за выбранный период)
    dates_period = []
    current_date = start_date
    while current_date.date() <= end_date.date():
        dates_period.append(current_date.date())
        current_date += datetime.timedelta(days=1)

    # format {'22.06.2025': {"Замена шин": 1, "Замена дисков": 3}
    jobtypes_count_in_date = {}

    for date in dates_period:
        jobtypes_count_in_date[f"{date}"] = {}

        # получаем кол-во работ для каждого jobtype в эту дату
        for jt in jobtypes:
            job_count = await AsyncOrm.get_jobs_count_by_jobtype_and_date(jt.id, date, session)

            if job_count != 0:
                jobtypes_count_in_date[f"{date}"][await t.t(jt.title, lang)] = job_count

    # строим график и получаем путь до него
    category_title = f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}"
    chart_path = jobtypes_for_category_graphic(jobtypes_count_in_date, category.id, category_title, start_date, end_date)

    # Удаляем сообщение об ожидании
    try:
        await waiting_message.delete()
    except:
        pass

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(
            photo=FSInputFile(chart_path),
        )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        text = await t.t("graphic_error", lang)

    # отправляем сообщение для дальнейшего выбора
    keyboard = await kb.back_keyboard(f"jobtype_select_done|work_categories_report|{period}", lang)

    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    # удаляем график
    try:
        os.remove(chart_path)
    except Exception as e:
        logger.error(f"Ошибка удаления графика {chart_path}: {e}")


# GRAPHIC INEFFICIENCY
@router.callback_query(F.data.split("|")[0] == "graphic-inefficiency")
async def inefficiency_graphic_report(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Отправка графика по неэффективности"""
    lang = r.get(f"lang:{tg_id}").decode()
    period = callback.data.split("|")[1]
    data = await state.get_data()

    # меняем предыдущее сообщение
    try:
        await data["prev_message"].edit_text(callback.message.text)
    except:
        pass

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # если был произвольный период
    if callback.data.split("|")[0] == "clndr":
        # формируем даты в формате datetime для дальнейшего сравнения
        data = await state.get_data()
        start_date = data["start_date"]
        end_date = convert_str_to_datetime(callback.data.split("|")[3])

        # меняем даты местами, если end_date меньше чем start_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)
    # данные для подписи оси Х (выписываем все даты за выбранный период)
    dates_period = []
    current_date = start_date
    while current_date.date() <= end_date.date():
        dates_period.append(current_date.strftime("%d.%m.%Y"))
        current_date += datetime.timedelta(days=1)

    data = {k: {} for k in dates_period}
    print(data)

    # From DB
    operations: list[OperationWithJobs] = await AsyncOrm.get_operations_with_jobs_and_transport_by_period(start_date, end_date, session)

    # Обрабатываем данные
    for o in operations:
        for job in o.jobs:
            key = f"{o.transport_subcategory}-{o.transport_serial_number} {await t.t(job.title, lang)}"

            if data[o.created_at.strftime("%d.%m.%Y")].get(key):
                data[o.created_at.strftime("%d.%m.%Y")][key] += 1
            else:
                data[o.created_at.strftime("%d.%m.%Y")][key] = 1

    # учитываем работы повторяющиеся только больше определенного количества раз за период
    if period == "today" or period == "yesterday":
        frequent_works = 1
    elif period == "week":
        frequent_works = 2
    elif period == "month":
        frequent_works = 5
    else:
        frequent_works = (end_date - start_date).days

    # Удаляем сообщение об ожидании
    try:
        await waiting_message.delete()
    except:
        pass

    chart_path = inefficiency_graphic(data, dates_period, frequent_works)

    # отправляем фото если получилось создать
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(
            photo=FSInputFile(chart_path),
        )
        text = await t.t("graphic_send", lang)

    # если график не удалось создать
    else:
        # text = await t.t("graphic_error", lang)
        text = f"За выбранный период {dates_period[0]} - {dates_period[-1]} нет неэффективных работ"

    # формируем callback для кнопки назад
    if period != "custom":
        back_callback = f"reports-period|inefficiency_report|{period}"
    else:
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        back_callback = f"clndr|inefficiency_report|{period}|{end_date_formatted}"

    # отправляем сообщение для дальнейшего выбора
    keyboard = await kb.back_keyboard(back_callback, lang)
    await callback.message.answer(text, reply_markup=keyboard.as_markup())

    if chart_path:
        # удаляем график
        try:
            os.remove(chart_path)
        except Exception as e:
            logger.error(f"Ошибка удаления графика {chart_path}: {e}")
