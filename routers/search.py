import difflib
from typing import Any


from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from schemas.search import OperationJobTransport, TransportNumber, OperationJobsUserLocation, ListOperations
from utils.translator import translator as t
from utils.date_time_service import get_dates_by_period

from routers.keyboards import search as kb
from routers.states.search import SearchWorkFSM
from routers.messages import search as ms

from database.orm import AsyncOrm

router = Router()


@router.callback_query(F.data.split("|")[1] == "search-vehicle")
async def search_vehicles_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню поиска транспорта старт FSM"""
    lang = r.get(f"lang:{tg_id}").decode()

    # начало FSM
    await state.set_state(SearchWorkFSM.enter_search_data)

    text = "🔍 " + await t.t("vehicle_history", lang) + "\n"
    message = text + await t.t("enter_transport_number", lang) + ":"

    keyboard = await kb.back_keyboard(lang, "menu|works-records")
    prev_message = await callback.message.edit_text(text=message, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(SearchWorkFSM.enter_search_data)
# возвращение с кнопки назад
@router.callback_query(SearchWorkFSM.period, F.data == "back_from_search_result")
async def get_data_to_search(message: types.Message | types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получение данных для поиска из сообщения"""
    lang = r.get(f"lang:{tg_id}").decode()

    # сообщение об ожидании
    if type(message) == types.Message:
        wait_message = await message.answer(await t.t("please_wait", lang))
    else:
        wait_message = await message.message.edit_text(await t.t("please_wait", lang))

    # меняем state
    await state.set_state(SearchWorkFSM.select_transport)

    data = await state.get_data()

    # удаляем предыдущее сообщение
    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    # формируем клавиатуру заранее
    keyboard = await kb.back_keyboard(lang, "works|search-vehicle")

    # проверяем только для прямого перехода
    if type(message) == types.Message:
        # если отправили не текст
        if not message.text:
            # сообщение о неправильно переданных данных
            text = await t.t("wrong_text_data", lang)
            await wait_message.edit_text(text, reply_markup=keyboard.as_markup())
            return

    # получаем из базы данных весь транспорт
    db_transports = await AsyncOrm.get_all_transports(session)

    # получаем из БД операции с транспортом и работами
    operations: list[OperationJobTransport] = await AsyncOrm.get_operations_with_jobs(session)

    # получаем текст от пользователя
    if type(message) == types.Message:
        text_from_message = message.text
        await state.update_data(text_from_message=text_from_message)

    # если пришли с callback берем сообщение из state
    else:
        text_from_message = data["text_from_message"]

    # проверяем на совпадение
    similar_transports = await get_match_transport_or_job(text_from_message, db_transports, operations, lang)

    # записываем данные для кнопки назад
    await state.update_data(similar_transports=similar_transports)

    # если совпадений нет
    if not similar_transports:
        # сообщение если совпадений нет
        text = await t.t("empty_search", lang)
        await wait_message.edit_text(text, reply_markup=keyboard.as_markup())
        return

    # если совпадения есть
    else:
        transports_for_keyboard: list[TransportNumber] = []
        # получаем совпавший транспорт из списка БД
        for transport in db_transports:
            if f"{transport.subcategory_title}-{transport.serial_number}" in similar_transports:
                transports_for_keyboard.append(transport)

    keyboard = await kb.transport_jobs_keyboard(lang, transports_for_keyboard)
    text = await t.t("select_found_vehicle", lang)
    await wait_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(SearchWorkFSM.select_transport, F.data.split("|")[0] == "searched_transport")
@router.callback_query(SearchWorkFSM.works_list, F.data.split("|")[0] == "searched_transport")  # для кнопки назад
async def select_transport(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Выбор периода для вывода работ"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(SearchWorkFSM.period)

    transport_id: str = callback.data.split("|")[1]

    # удаляем старый кэш
    r.delete(f"searched-operations|{transport_id}")

    # записываем выбранный транспорт
    await state.update_data(transport_id=transport_id)

    text = await t.t("select_period", lang)
    keyboard = await kb.transport_period_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "search_period", SearchWorkFSM.period)
@router.callback_query(F.data.split("|")[0] == "search_period", SearchWorkFSM.works_list)   # для кнопки назад
async def select_period(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Получаем выбранный пользователем период и выводим список работ по транспорту"""
    lang = r.get(f"lang:{tg_id}").decode()
    period: str = callback.data.split("|")[1]

    # сообщение об ожидании
    wait_mess = await callback.message.edit_text(await t.t("please_wait", lang))

    # сохраняем период для дальнейшей передачи
    await state.update_data(period=period)

    # меняем state
    await state.set_state(SearchWorkFSM.works_list)

    data = await state.get_data()
    transport_id = int(data["transport_id"])

    start_date, end_date = get_dates_by_period(period)

    operations_for_transport: ListOperations = await AsyncOrm.get_operations_jobs_user_for_transport(
        transport_id, start_date, end_date, session
    )

    # если работ нет -> возвращаемся к выбору периода
    if not operations_for_transport:
        keyboard = await kb.back_keyboard(lang, f"searched_transport|{transport_id}")
        await wait_mess.edit_text(await t.t("empty_works", lang), reply_markup=keyboard.as_markup())
        return

    # записываем кэш
    operations_for_transport_json = operations_for_transport.model_dump_json()
    r.set(f"searched-operations|{transport_id}", operations_for_transport_json)

    message = await ms.search_transport_result(operations_for_transport.operations, lang)
    keyboard = await kb.found_operations_keyboard(operations_for_transport.operations, lang, f"searched_transport|{transport_id}")

    await wait_mess.edit_text(message, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "operation-detail", SearchWorkFSM.works_list)
async def select_period(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Выводим детали выбранной работы"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    period = data["period"]
    transport_id = int(data["transport_id"])
    operation_id = int(callback.data.split("|")[1])

    # получаем все операции по этому транспорту за выбранный период из кэша
    cached_data = r.get(f"searched-operations|{transport_id}")
    list_operations = ListOperations.model_validate_json(cached_data)

    # заглушка для message
    message = "Something goes wrong"

    # выбираем нужную нам
    for operation in list_operations.operations:
        if operation.id == operation_id:
            message = await ms.operation_detail_message(operation, lang)

    keyboard = await kb.back_and_main_menu_keyboard(f"search_period|{period}", lang)

    await callback.message.edit_text(message, reply_markup=keyboard.as_markup())

    # удаляем кэш
    r.delete(f"searched-operations|{transport_id}")


async def get_match_transport_or_job(
        input_data: str, transports: list[TransportNumber], operations: [OperationJobTransport], lang: str
) -> list[str]:
    """Парсит введенные данные и возвращает варианты для дальнейшего поиска"""
    # формируем названия транспорта
    transport_names = [f"{transport.subcategory_title}-{transport.serial_number}" for transport in transports]

    # переводим работы в нужный язык
    translated_jobs = {op.id: await t.t(op.job_title, lang) for op in operations}

    transports: list[str] = []  # полные названия совпавших работ U-12, SS-1 ...

    # если в тексте есть цифра, то проверяем и на работы и на транспорт
    if any(char.isdigit() for char in input_data):
        # делим присланные данные для более подробного поиска
        input_data_split = input_data.split(" ")

        for word in input_data_split:

            # проверяем переданные слова на наличие в нем транспорта и добавляем к предполагаемому транспорту
            transports.extend(difflib.get_close_matches(word, transport_names, n=2, cutoff=0.3))

    # если цифр нет, то проверяем только на работы
    else:
        # проверяем jobs
        matches_titles = difflib.get_close_matches(input_data, translated_jobs.values(), n=2)
        for key, value in translated_jobs.items():
            if value in matches_titles:
                for op in operations:
                    if op.id == key:
                        transports.append(f"{op.transport_subcategory}-{op.serial_number}")
                        break

    return transports
