import datetime
from typing import Any

from aiogram import Router, F, types

from cache import r
from utils.translator import translator as t

from routers.keyboards.works import works_menu_keyboard
from routers.keyboards import my_works as kb
from routers.messages import my_works as ms
from schemas.operations import OperationShow, OperationDetails

from database.orm import AsyncOrm

router = Router()


@router.callback_query(F.data.split("|")[1] == "works-records")
async def works_reports_menu(callback: types.CallbackQuery) -> None:
    """Меню учета выполненных работ"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    text = "📋 " + await t.t("work_records", lang)

    keyboard = await works_menu_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[1] == "my-works")
async def my_works_period(callback: types.CallbackQuery, tg_id: str) -> None:
    """Мои работы выбор периода"""
    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t("select_period", lang)
    keyboard = await kb.works_period_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "my-works")
async def my_works_list(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Вывод списка работ за выбранный период"""
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем выбранный период и формируем start/end период выборки
    period = callback.data.split("|")[1]

    if period == "today":
        start_period = datetime.datetime.now().date()   # делаем только дату без времени
        end_period = datetime.datetime.now()

    elif period == "yesterday":
        start_period = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        end_period = datetime.datetime.strptime(start_period.strftime("%Y-%m-%d") + " 23:59:59", "%Y-%m-%d %H:%M:%S")

    elif period == "week":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=7)

    elif period == "month":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=30)  # ставим для месяца 30 дней

    else:
        # TODO заглушка
        end_period = datetime.datetime.now()
        start_period = datetime.datetime.now()
        await callback.message.edit_text("Введите кастомный период")
        return

    # получаем Operations
    operations: list[OperationShow] = await AsyncOrm.select_operations(start_period, end_period, tg_id, session)

    # формируем клавиатуру
    keyboard = await kb.works_my_works_list(lang, operations, period)

    # если еще нет работ
    if not operations:
        text = await t.t("empty_works", lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
        return

    text = await t.t("works_list", lang)

    # TODO пагинация
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "my-works-list")
async def work_detail(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Вывод подробного описания работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    # период получаем из колбэка (чтобы потом можно было кнопку назад сделать)
    period = callback.data.split("|")[2]

    operation_id = int(callback.data.split("|")[1])

    operation: OperationDetails = await AsyncOrm.select_operation(operation_id, session)

    message = await ms.work_detail_message(lang, operation)
    keyboard = await kb.work_details(lang, operation_id, period)

    await callback.message.edit_text(message, reply_markup=keyboard.as_markup())
