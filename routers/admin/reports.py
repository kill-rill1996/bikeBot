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
    InefficiencyReport
from utils.excel_reports import individual_mechanic_excel_report
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

    # количество работ
    jobs_count = sum([len(operation.jobs) for operation in operations])
    text += await t.t("number_of_works", lang) + " " + f"<b>{str(jobs_count)}</b>" + "\n"

    # количество потраченного времени
    duration_sum = str(sum([operation.duration for operation in operations]))
    text += await t.t("total_time_spent", lang) + " " + f"<b>{duration_sum}</b>" + " " + await t.t("minutes", lang) + "\n\n"

    # Список всех работ с деталями
    text += await t.t("work_list", lang) + "\n"
    for idx, operation in enumerate(operations, start=1):
        date, time = convert_date_time(operation.created_at, with_tz=True)
        row_text = f"<b>{idx})</b> ID {operation.id} | {date} {time} | {str(operation.duration)} {await t.t('minutes', lang)} | " \
                   f"{await t.t(operation.transport_category, lang)} {operation.transport_subcategory}-{operation.transport_serial_number}\n"

        # группа узлов
        row_text += await t.t(operation.jobs[0].jobtype_title, lang) + ":\n"

        # jobs для каждой операции
        for job in operation.jobs:
            row_text += "\t\t• " + await t.t(job.title, lang) + "\n"

        # комментарий
        comment = operation.comment if operation.comment else "-"
        row_text += f'{await t.t("comment", lang)} <i>"{comment}"</i>\n'

        # среднее время на одну работу
        row_text += await t.t("avg_time", lang) + " " + f"{round(operation.duration / len(operation.jobs))} " + await t.t("minutes", lang)

        text += row_text + "\n\n"

    keyboard = await kb.mechanic_report_details_keyboard(period, "individual_mechanic_report", user_id, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


# 📆 Сводный отчет по механикам
@router.callback_query(F.data.split("|")[0] == "reports-period" and F.data.split("|")[1] == "summary_report_by_mechanics")
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

        # записываем обе даты в стейт
        await state.update_data(start_date=start_date)
        await state.update_data(end_date=end_date)

    # не произвольный период
    else:
        start_date, end_date = get_dates_by_period(period)

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

    keyboard = await kb.summary_report_details_keyboard(report_type, lang)
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
    for idx, operation in enumerate(operations, start=1):
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
async def vehicle_report_by_subcategory_choose_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Выбор подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]

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
    for idx, operation in enumerate(operations, start=1):
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
async def vehicle_report_by_transport_choose_category(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Выбор категории для отчета по серийному номеру транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[2]
    period = callback.data.split("|")[3]

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
    for idx, operation in enumerate(operations, start=1):
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

    await state.clear()

    jobtypes = await AsyncOrm.get_jobtypes_by_ids(selected_jobtypes, session)

    # получаем даты в зависимости от периода
    if period != "custom":
        start_date, end_date = get_dates_by_period(period)
    else:
        start_date = data["start_date"]
        end_date = data["end_date"]

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
            row_text += f"{await t.t(k, lang)} {v}\n"

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
    # TODO для custom_period
    else:
        frequent_works = 10

    row_text = ""
    for k, v in sorted_jobs.items():
        if v >= frequent_works:
            row_text += "\t\t• " + k + f": {v}" + "\n"

    # повторяющиеся работы за период
    if row_text:
        text += await t.t("repeatable_jobs", lang) + "\n"
        text += row_text + "\n"
    # else:
    #     text += await t.t('no_operations', lang) + "\n"

    # операции без комментариев
    text += await t.t("no_comments", lang) + "\n"
    for o in operations:
        if not o.comment:
            date, time = convert_date_time(o.created_at, with_tz=True)
            row_text = f"{date} {time} | ID {o.id} | " \
                       f"{o.transport_subcategory}-{o.transport_serial_number}\n"
            text += row_text

    keyboard = await kb.efficient_report_details_keyboard(report_type, lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "excel_export")
async def send_excel_file(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Отправка эксель файла для типа отчета"""
    lang = r.get(f"lang:{tg_id}").decode()
    report_type = callback.data.split("|")[1]
    period = callback.data.split("|")[2]

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))
    data = await state.get_data()
    start_date = data["start_date"]
    end_date = data["end_date"]

    # 📆 Индивидуальный отчет по механику
    if report_type == "individual_mechanic_report":
        # получаем данные для отчета
        user_id = int(callback.data.split("|")[3])
        user = await AsyncOrm.get_user_by_id(user_id, session)
        operations = await AsyncOrm.get_operations_for_user_by_period(user.tg_id, start_date, end_date, session)

        # если нет операций
        if not operations:
            msg_text = await t.t("no_operations", lang)
            keyboard = await kb.back_to_mechanic(period, report_type, lang)
            await waiting_message.edit_text(msg_text, reply_markup=keyboard.as_markup())
            return

        # путь до отчета
        file_path = await individual_mechanic_excel_report(operations, user.username, start_date, end_date, report_type, lang)
        document = FSInputFile(file_path)

        # отправляем отчет
        await waiting_message.delete()
        start_date_formatted = convert_date_time(start_date, with_tz=True)[0]
        end_date_formatted = convert_date_time(end_date, with_tz=True)[0]
        text = f"{await t.t('individual_mechanic_report', lang)} {start_date_formatted} - {end_date_formatted}"
        await callback.message.answer_document(document, caption=text)

        # отправляем сообщение с клавиатурой
        text = await t.t("excel_ready", lang)
        back_callback = f"mechanic|{period}|{user_id}"
        keyboard = await kb.excel_ready_keyboard(back_callback, lang)
        await callback.message.answer(text, reply_markup=keyboard.as_markup())

        # удаляем отчет
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Не удалось удалить файл с отчетом {file_path}: {e}")










