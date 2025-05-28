# works|works-statistic
import datetime
from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import statistic as kb
from routers.messages import statistic as ms
from schemas.operations import OperationJobs
from utils.translator import translator as t
from utils.date_time_service import get_dates_by_period
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
async def works_statistic_for_period(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Вывод статистики за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()

    # сообщение об ожидании
    wait_message = await callback.message.edit_text(await t.t("please_wait", lang))

    # получаем необходимый период
    period = callback.data.split("|")[1]
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

