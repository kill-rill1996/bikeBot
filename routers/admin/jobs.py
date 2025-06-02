from typing import Any

from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from cache import r
from routers.states.jobs import AddJobtype
from schemas.categories_and_jobs import Category
from utils.translator import translator as t, neet_to_translate_on
from database.orm import AsyncOrm
from routers.keyboards import jobs as kb

router = Router()


@router.callback_query(F.data == "admin|operation_management")
async def jobs_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню управления операциями"""
    lang = r.get(f"lang:{tg_id}").decode()

    # Скидывем state
    try:
        await state.clear()
    except Exception:
        pass

    text = f"🛠 {await t.t('operation_management', lang)}"

    keyboard = await kb.jobs_management_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD / EDIT JOB_TYPE
@router.callback_query(F.data == "jobs-management|add_jobtype")
async def add_jobtype(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Запрос типа операции"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(AddJobtype.input_jobtype)

    text = await t.t("input_jobtype", lang)
    keyboard = await kb.back_keyboard(lang, "admin|operation_management")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(or_f(AddJobtype.input_jobtype))
async def get_jobtype(message: types.Message, tg_id, state: FSMContext, session: Any) -> None:
    """Получение типа"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    try:
        await data["prev_message"].delete()
    except:
        pass

    keyboard = await kb.back_keyboard(lang, "jobs-management|add_jobtype")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    text_from_message = message.text

    # from DB
    categories: [Category] = await AsyncOrm.get_all_categories(session)

    await state.set_state(AddJobtype.select_categories)

    await state.update_data(text_from_message=text_from_message)
    # for multiselect
    await state.update_data(selected_categories=[])
    await state.update_data(categories_for_select=categories)

    text = await t.t("for_which_transport", lang)
    keyboard = await kb.categories_keyboard(categories, [], lang)

    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add-jobtype-select", AddJobtype.select_categories)
async def multiselect_categories(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Мультиселект категорий"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    # добавляем или удаляем категорию из списка
    data = await state.get_data()
    selected_categories = data["selected_categories"]
    categories_for_select = data["categories_for_select"]

    # удаляем если уже есть
    if category_id in selected_categories:
        selected_categories.remove(category_id)
    # добавляем если нет
    else:
        selected_categories.append(category_id)

    await state.update_data(selected_categories=selected_categories)

    text = await t.t("for_which_transport", lang)
    keyboard = await kb.categories_keyboard(categories_for_select, selected_categories, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "select_categories_done", AddJobtype.select_categories)
async def get_translate_1(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(AddJobtype.translate_1)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    keyboard = await kb.back_keyboard(lang, "back-from-translate_1")
    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())











