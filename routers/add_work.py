from typing import Any

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from utils.translator import translator as t
from utils.validations import is_valid_vehicle_number
from routers.states.add_work import AddWorkFSM
from database.orm import AsyncOrm

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

    # TODO убрать если ненужно
    # # категория не велосипед
    # else:
    #     # пропускаем подкатегорию, номер и переходим в стейт AddWorkFSM.work_category
    #     await state.set_state(AddWorkFSM.work_category)
    #
    #     text = t.t("select_work_category", lang)
    #     await callback.message.edit_text(text, reply_markup=kb.select_work_category(lang).as_markup())


@router.callback_query(F.data.split("|")[0] == "vehicle_subcategory", AddWorkFSM.vehicle_subcategory)
async def add_work_vehicle_subcategory(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись подкатегории. Выбор номера"""
    vehicle_subcategory_id = int(callback.data.split("|")[1])
    vehicle_subcategory_title = callback.data.split("|")[2]
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # записываем подкатегорию
    await state.update_data(subcategory_id=vehicle_subcategory_id)
    await state.update_data(subcategory_title=vehicle_subcategory_title)

    # меняем стейт
    await state.set_state(AddWorkFSM.vehicle_number)

    # TODO перевести текст для всех
    text = f"Введите номер велосипеда для подкатегории {vehicle_subcategory_title}"

    keyboard = await kb.select_bicycle_number(lang)
    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddWorkFSM.vehicle_number)
async def add_work_vehicle_number(message: types.Message, state: FSMContext, session: Any) -> None:
    """Валидация и запись номера и запись его в стейт"""
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
        keyboard = await kb.select_bicycle_number(lang)
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

        keyboard = await kb.select_work_category(jobtypes, lang)
        await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "work_jobtype", AddWorkFSM.jobtype)
async def add_work_category(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запись категории работы"""
    jobtype_id = int(callback.data.split("|")[1])
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    # записываем категорию работы
    await state.update_data(jobtype_id=jobtype_id)

    text = await t.t("select_operation", lang)
    await callback.message.edit_text(text)


