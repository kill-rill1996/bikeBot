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

from routers.keyboards import add_works as kb

router = Router()


@router.callback_query(F.data == "works|add-works")
async def add_work_menu(callback: types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Меню добавить работу. Меню выбора категории"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    categories = await AsyncOrm.get_all_categories(session)

    # начало стейта AddWorkFSM
    await state.set_state(AddWorkFSM.vehicle_category)

    text = await t.t("select_category", lang)
    keyboard = await kb.add_works_menu_keyboard(categories, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_category", AddWorkFSM.vehicle_category)
@router.callback_query(F.data.split("|")[0] == "back_to_choose_subcategory")
async def add_work_vehicle_category(callback: types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Запись категории. Меню выбора подкатегории"""
    vehicle_category_id = int(callback.data.split("|")[1])
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем подкатегории
    subcategories = await AsyncOrm.get_subcategories_by_category(vehicle_category_id, session)

    # запись категории в стейт
    await state.update_data(category_id=vehicle_category_id)

    # устанавливаем стейт
    await state.set_state(AddWorkFSM.vehicle_subcategory)

    # предлагаем выбрать подкатегорию
    text = await t.t("select_subcategory", lang)

    keyboard = await kb.select_subcategory_keyboard(subcategories, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_subcategory", AddWorkFSM.vehicle_subcategory)
async def add_work_vehicle_subcategory(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись подкатегории. Выбор номера"""
    subcategory_id = int(callback.data.split("|")[1])
    subcategory_title = callback.data.split("|")[2]
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # записываем подкатегорию
    await state.update_data(subcategory_id=subcategory_id)
    await state.update_data(subcategory_title=subcategory_title)

    # меняем стейт
    await state.set_state(AddWorkFSM.vehicle_number)

    # TODO перевести текст для всех
    text = f"Введите номер велосипеда для подкатегории {subcategory_title}"

    # category_id нужна для кнопки назад
    data = await state.get_data()
    category_id = data["category_id"]
    keyboard = await kb.select_bicycle_number(category_id, lang)

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddWorkFSM.vehicle_number)
@router.callback_query(F.data.split("|")[0] == "back_to_jobtype")
async def add_work_vehicle_number(message: types.Message | types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Валидация и запись номера и запись его в стейт"""
    # прямой путь
    if type(message) == types.Message:
        serial_number = message.text
        tg_id = str(message.from_user.id)
        lang = r.get(f"lang:{tg_id}").decode()

        # удаляем предыдущее сообщение
        data = await state.get_data()
        try:
            await data["prev_mess"].delete()
        except Exception:
            pass

        # номера для данной категории и подкатегории
        category_id = data["category_id"]
        subcategory_id = data["subcategory_id"]
        serial_numbers = await AsyncOrm.get_sn_by_category_and_subcategory(category_id, subcategory_id, session)

        # если номер неправильный
        if not is_valid_vehicle_number(serial_number, serial_numbers):
            # отправляем сообщение о необходимости ввести номер еще раз
            # TODO перевод!!! и поправить сообщение по смыслу
            text = f"Номер введен неправильно для категории {data['subcategory_title']}\n" \
                   f"Необходимо отправить число от 1 до 100, отправьте номер еще раз"
            keyboard = await kb.select_bicycle_number(category_id, lang)
            msg = await message.answer(text, reply_markup=keyboard.as_markup())

            # записываем в предыдущие сообщения
            await state.update_data(prev_mess=msg)

        # если номер правильный
        else:
            # записываем номер в стейт
            await state.update_data(serial_number=int(serial_number))

            # переходим в стейт AddWorkFSM.work_category
            await state.set_state(AddWorkFSM.jobtype)

            # получаем группы узлов для этой категории
            jobtypes = await AsyncOrm.get_job_types_by_category(category_id, session)

            text = await t.t("select_work_category", lang)

            keyboard = await kb.select_work_category(jobtypes, category_id, lang)
            await message.answer(text, reply_markup=keyboard.as_markup())

    # если вернулись назад с job (callback)
    else:
        category_id = int(message.data.split("|")[1])
        tg_id = str(message.from_user.id)
        lang = r.get(f"lang:{tg_id}").decode()

        # переходим в стейт AddWorkFSM.work_category
        await state.set_state(AddWorkFSM.jobtype)

        # получаем группы узлов для этой категории
        jobtypes = await AsyncOrm.get_job_types_by_category(category_id, session)

        text = await t.t("select_work_category", lang)

        keyboard = await kb.select_work_category(jobtypes, category_id, lang)
        await message.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "work_jobtype", AddWorkFSM.jobtype)
@router.callback_query(F.data.split("|")[0] == "back_to_work_jobtype")
async def add_work_category(callback: types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Запись категории работы"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # для кнопок назад
    if callback.data.split("|")[0] == "work_jobtype":
        jobtype_id = int(callback.data.split("|")[1])
        # записываем категорию работы
        await state.update_data(jobtype_id=jobtype_id)
    else:
        jobtype_id = data["jobtype_id"]

    # добавляем список для мультиселекта
    await state.update_data(selected_jobs=[])

    # меняем стейт
    await state.set_state(AddWorkFSM.job)

    # получаем jobs для этого jobtype
    jobs = await AsyncOrm.get_all_jobs_by_jobtype_id(jobtype_id, session)

    text = await t.t("select_operation", lang)

    # category_id необходимо, чтобы создать кнопку назад
    category_id = data["category_id"]
    page = 1
    keyboard = await kb.select_jobs_keyboard(jobs, page, category_id, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "work_job_select", AddWorkFSM.job)
async def job_multiselect(callback: types.CallbackQuery, state: FSMContext, session) -> None:
    """Вспомогательный хэндлер для мультиселекта"""
    job_id = int(callback.data.split("|")[1])
    page = int(callback.data.split("|")[2])
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # добавляем или удаляем работу из списка
    data = await state.get_data()
    selected_jobs = data["selected_jobs"]
    # удаляем если уже есть
    if job_id in selected_jobs:
        selected_jobs.remove(job_id)
    # добавляем если нет
    else:
        selected_jobs.append(job_id)
    await state.update_data(selected_jobs=selected_jobs)

    # получаем jobs для этого jobtype
    jobs = await AsyncOrm.get_all_jobs_by_jobtype_id(data["jobtype_id"], session)

    text = await t.t("select_operation", lang)

    # сообщение
    category_id = data["category_id"]
    keyboard = await kb.select_jobs_keyboard(jobs, page, category_id, lang, selected_jobs)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "prev", AddWorkFSM.job)
@router.callback_query(F.data.split("|")[0] == "next", AddWorkFSM.job)
async def pagination_handler(callback: types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Вспомогательный хендлер для пагинации"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # wait message
    wait_text = await t.t("please_wait", lang)
    wait_message = await callback.message.edit_text(wait_text)

    action = callback.data.split("|")[0]
    current_page = int(callback.data.split("|")[1])

    # меняем номер страницы
    if action == "prev":
        page = current_page - 1
    else:
        page = current_page + 1

    # получаем jobs для этого jobtype
    data = await state.get_data()
    jobtype_id = data["jobtype_id"]
    jobs = await AsyncOrm.get_all_jobs_by_jobtype_id(jobtype_id, session)

    # для мультиселекта
    selected_jobs = data["selected_jobs"]

    text = await t.t("select_operation", lang)
    # category_id необходимо, чтобы создать кнопку назад
    category_id = data["category_id"]
    keyboard = await kb.select_jobs_keyboard(jobs, page, category_id, lang, selected_jobs)
    await wait_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "work_job_done", AddWorkFSM.job)
@router.callback_query(F.data.split("|")[0] == "back_to_work_job")
async def add_work_duration(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Отправка сообщения записи времени"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем стейт
    await state.set_state(AddWorkFSM.duration)

    text = await t.t("how_long", lang)

    # для кнопки назад
    data = await state.get_data()
    jobtype_id = data["jobtype_id"]
    keyboard = await kb.back_from_duration(jobtype_id, lang)

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddWorkFSM.duration)
@router.callback_query(F.data.split("|")[0] == "back_to_work_location")
async def get_duration(message: types.Message | types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Проверка правильности времени"""
    tg_id = str(message.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # прямой порядок
    if type(message) == types.Message:
        duration = message.text

        try:
            await data["prev_mess"].delete()
        except Exception:
            pass

        # неправильное число
        if not is_valid_duration(duration):
            jobtype_id = data["jobtype_id"]
            text = await t.t("duration_error", lang)
            keyboard = await kb.back_from_duration(jobtype_id, lang)
            await message.answer(text, reply_markup=keyboard.as_markup())

        # правильное число
        else:
            # записываем время в стейт
            await state.update_data(duration=int(duration))

            # меняем стейт
            await state.set_state(AddWorkFSM.location)

            # получаем локации
            locations = await AsyncOrm.get_locations(session)

            text = await t.t("current_location", lang)
            keyboard = await kb.select_location(locations, lang)
            await message.answer(text, reply_markup=keyboard.as_markup())

    # назад с ввода комментария
    else:
        # меняем стейт
        await state.set_state(AddWorkFSM.location)

        # получаем локации
        locations = await AsyncOrm.get_locations(session)

        text = await t.t("current_location", lang)
        keyboard = await kb.select_location(locations, lang)
        await message.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "work_location", AddWorkFSM.location)
async def get_location(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись локации"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()
    location_id = int(callback.data.split("|")[1])

    # записываем location
    await state.update_data(location_id=location_id)

    # меняем стейт
    await state.set_state(AddWorkFSM.comment)

    # для кнопки назад
    data = await state.get_data()
    duration = data["duration"]

    # предлагаем отправить комментарий
    text = await t.t("add_description", lang)
    keyboard = await kb.back_from_comment_keyboard(duration, lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddWorkFSM.comment)
@router.callback_query(F.data == "continue", AddWorkFSM.comment)
async def get_comment(message: types.Message | types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Запись комментария. Предпросмотр"""
    tg_id = str(message.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # при наличии комментария
    if type(message) == types.Message:
        # удаляем предыдущее сообщение
        try:
            await data["prev_mess"].delete()
        except Exception:
            pass

        comment = message.text
        wait_text = await t.t("please_wait", lang)
        waiting_message = await message.answer(wait_text)

    # при отсутствии комментария
    else:
        comment = None
        wait_text = await t.t("please_wait", lang)
        waiting_message = await message.message.edit_text(wait_text)

    # записываем коммент в стейт
    await state.update_data(comment=comment)

    # меняем стейт
    await state.set_state(AddWorkFSM.confirmation)

    # ПРЕДПРОСМОТР
    text = await t.t("preview", lang) + "\n"

    # дата
    current_date = convert_date_time(datetime.datetime.now(), settings.timezone)[0]
    date_text = await t.t("date", lang)
    text += date_text + " " + current_date + "\n"

    # category
    category = await AsyncOrm.get_category_by_id(data["category_id"], session)
    subcategory = await AsyncOrm.get_subcategory_by_id(data["subcategory_id"], session)
    text += await t.t(category.title, lang) + ": " + subcategory.title + "-" + str(data["serial_number"]) + "\n"

    # operation
    jobtype = await AsyncOrm.get_jobtype_by_id(data["jobtype_id"], session)
    jobtype_title = await t.t(jobtype.title, lang)

    # todo поправить список
    jobs = await AsyncOrm.get_jobs_by_ids([data["job_id"]], session)
    jobs_text = ""
    for job in jobs:
        jobs_text += await t.t(job.title, lang) + " "

    text += await t.t("operation", lang) + " " + jobtype_title + " → " + jobs_text + "\n"

    # time
    text += await t.t("time", lang) + " " + str(data["duration"]) + " " + await t.t("minutes", lang) + "\n"

    # comment
    comment_text = comment if comment else "-"
    text += await t.t("comment", lang) + " " + comment_text

    keyboard = await kb.preview_keyboard(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(AddWorkFSM.confirmation)
async def confirmation(callback: types.CallbackQuery, state: FSMContext, admin: bool, session: Any) -> None:
    """Подтверждение или отмена"""
    # при отмене
    if callback.data == "cancel":
        await show_main_menu(callback, admin, state)
        return

    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # проверка дублирования
    transport_id = await AsyncOrm.get_transport_id(data["category_id"], data["subcategory_id"], data["serial_number"], session)
    operation: Operation | None = await AsyncOrm.get_operation_by_params(transport_id, data["job_id"], data["location_id"], session)

    # если такая работа уже была
    if operation:
        # меняем стейт
        await state.set_state(AddWorkFSM.second_confirmation)

        text = await t.t("already_performed", lang)

        # job
        jobs = await AsyncOrm.get_jobs_by_ids([data["job_id"]], session)
        jobs_text = ", ".join([job.title for job in jobs])
        # subcategory
        subcategory = await AsyncOrm.get_subcategory_by_id(data["subcategory_id"], session)
        # serial_number
        serial_number = str(data["serial_number"])
        formatted_text = text.format(jobs_text, subcategory.title, serial_number)

        keyboard = await kb.second_confirmation_keyboard(lang)
        await callback.message.edit_text(formatted_text, reply_markup=keyboard.as_markup())

    # если работы не было
    else:
        text = await t.t("work_save", lang)
        keyboard = await kb.work_saved_keyboard(lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

        # сброс стейта
        await state.clear()

        # запись operation в БД
        transport_id = await AsyncOrm.get_transport_id(data["category_id"], data["subcategory_id"],
                                                       data["serial_number"], session)

        operation_add = OperationAdd(
            tg_id=tg_id,
            transport_id=int(transport_id),
            job_id=data["job_id"],
            duration=data["duration"],
            location_id=data["location_id"],
            comment=data["comment"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        await AsyncOrm.create_operation(operation_add, session)


@router.callback_query(AddWorkFSM.second_confirmation)
async def second_confirmation(callback: types.CallbackQuery, state: FSMContext, admin: bool, session: Any) -> None:
    """Подтверждение недублирования операции"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # подтверждение, что не дубликат
    if callback.data == "yes":
        data = await state.get_data()

        text = await t.t("work_save", lang)
        keyboard = await kb.work_saved_keyboard(lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

        # сброс стейта
        await state.clear()

        # запись operation в БД
        transport_id = await AsyncOrm.get_transport_id(data["category_id"], data["subcategory_id"],
                                                       data["serial_number"], session)

        operation_add = OperationAdd(
            tg_id=tg_id,
            transport_id=int(transport_id),
            job_id=data["job_id"],
            duration=data["duration"],
            location_id=data["location_id"],
            comment=data["comment"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        await AsyncOrm.create_operation(operation_add, session)

    # если дубликат
    else:
        await state.clear()
        await show_main_menu(callback, admin, state)









