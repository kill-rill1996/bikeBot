import datetime
from typing import Any

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import statistic as kb
from routers.messages import statistic as ms
from routers.states.statistics import StatisticsCustomPeriod
from schemas.operations import OperationJobs
from utils.translator import translator as t
from utils.date_time_service import get_dates_by_period, get_next_and_prev_month_and_year, convert_str_to_datetime, \
    convert_date_time
from cache import r

router = Router()


@router.callback_query(F.data == "works|works-statistic")
async def statistic_menu(callback: types.CallbackQuery, tg_id: str) -> None:
    """Меню статистики"""
    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t("select_period", lang)
    keyboard = await kb.statistic_period_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "works-statistic")
async def works_statistic_for_period(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Вывод статистики за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()

    # сообщение об ожидании
    wait_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем необходимый период
    period = callback.data.split("|")[1]

    # для кастомного периода
    if period == "custom-period":
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month
        dates_data = get_next_and_prev_month_and_year(now_month, now_year)

        text = await t.t("select_date_start", lang)
        keyboard = await kb.select_custom_date(now_year, now_month, lang, dates_data=dates_data)

        # начинаем FSM
        await state.set_state(StatisticsCustomPeriod.period)
        await wait_message.edit_text(text, reply_markup=keyboard.as_markup())

    # для всех других периодов
    else:
        start_date, end_date = get_dates_by_period(period)

        # получение категорий транспорта для формирования сообщения
        transports = await AsyncOrm.get_all_categories(session)

        # получение необходимых данных по статистике работа
        operations: list[OperationJobs] = await AsyncOrm.select_operations(start_date, end_date, tg_id, session)

        # получаем клавиатуру
        keyboard = await kb.statistic_view_keyboard(lang)

        # если нет работ
        if not operations:
            await wait_message.edit_text(await t.t("empty_works", lang), reply_markup=keyboard.as_markup())
            return

        text = await t.t("statistic_view", lang) + "\n\n"
        message = text + await ms.statistic_message(lang, operations, transports)

        await wait_message.edit_text(message, reply_markup=keyboard.as_markup())


# ONLY FOR CUSTOM
@router.callback_query(F.data.split("|")[0] == "statistic_end_date")
@router.callback_query(F.data.split("|")[0] == "st_action")
async def get_custom_period(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Обработка кастомного периода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # для выбора второй даты
    if callback.data.split("|")[0] == "statistic_end_date":

        # собираем первую дату
        start_date_str = callback.data.split("|")[1]
        start_date = convert_str_to_datetime(start_date_str)

        # устанавливаем стейт для каждого отчета отдельно
        await state.set_state(StatisticsCustomPeriod.end_date)

        # записываем первую дату в стейт
        await state.update_data(start_date=start_date)

        # данные для формирования клавиатуры
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month
        dates_data = get_next_and_prev_month_and_year(now_month, now_year)

        text = await t.t("select_date_end", lang) + f"\n{convert_date_time(start_date, with_tz=True)[0]}-"
        keyboard = await kb.select_custom_date(now_year, now_month, lang, dates_data=dates_data, end_date=True)

    # для выбора первой даты
    elif callback.data.split("|")[0] == "reports-period" and callback.data.split("|")[2] == "custom":
        # данные для формирования клавиатуры
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month
        dates_data = get_next_and_prev_month_and_year(now_month, now_year)

        text = await t.t("select_date_start", lang)
        keyboard = await kb.select_custom_date(now_year, now_month, lang, dates_data=dates_data)

        # для перелистывания месяцев
    else:
        month = int(callback.data.split("|")[1])
        year = int(callback.data.split("|")[2])

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

        keyboard = await kb.select_custom_date(year, month, lang, dates_data=dates_data, end_date=end_date)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "st_clndr", StatisticsCustomPeriod.end_date)
async def statistics_custom_period(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Вывод статистики за кастомный периоде"""
    lang = r.get(f"lang:{tg_id}").decode()

    # формируем даты в формате datetime для дальнейшего сравнения
    data = await state.get_data()
    start_date = data["start_date"]
    end_date = convert_str_to_datetime(callback.data.split("|")[2])

    # меняем даты местами, если end_date меньше чем start_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # записываем обе даты в стейт
    await state.update_data(start_date=start_date)
    await state.update_data(end_date=end_date)

    # получение категорий транспорта для формирования сообщения
    transports = await AsyncOrm.get_all_categories(session)

    # получение необходимых данных по статистике работа
    operations: list[OperationJobs] = await AsyncOrm.select_operations(start_date, end_date, tg_id, session)

    # получаем клавиатуру
    keyboard = await kb.statistic_view_keyboard(lang)

    # если нет работ
    if not operations:
        await callback.edit_text(await t.t("empty_works", lang), reply_markup=keyboard.as_markup())
        return

    text = await t.t("statistic_view", lang) + "\n\n"
    message = text + await ms.statistic_message(lang, operations, transports)

    await callback.message.edit_text(message, reply_markup=keyboard.as_markup())
