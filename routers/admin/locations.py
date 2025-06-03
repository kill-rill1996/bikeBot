from typing import Any

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import locations as kb
from routers.states.locations import AddLocationFSM, EditLocationFSM
from schemas.location import Location
from utils.translator import translator as t, neet_to_translate_on
from cache import r

router = Router()


@router.callback_query(F.data == "admin|location_management")
async def location_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню управления местоположением"""
    try:
        await state.clear()
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()

    text = f"🌎 {await t.t('location_management', lang)}"

    keyboard = await kb.location_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "show_locations")
async def location_menu(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Список локаций"""
    lang = r.get(f"lang:{tg_id}").decode()

    locations = await AsyncOrm.get_locations(session)

    # если локаций нет
    if not locations:
        text = t.t("no_locations", lang)
        keyboard = await kb.back_and_main_menu(lang)
        await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
        return

    # если локации есть
    text = f'<b>{await t.t("all_locations", lang)}</b>\n\n'
    for idx, location in enumerate(locations, start=1):
        text += f"<b>{idx})</b> {await t.t(location.name, lang)}\n"

    keyboard = await kb.back_and_main_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "add_location")
async def start_add_location(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Добавление локации"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(AddLocationFSM.input_name)

    text = await t.t("set_name", lang)

    keyboard = await kb.cancel_keyboard(lang)

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddLocationFSM.input_name)
async def get_location_name(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Запись имени локации"""
    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    location_name = message.text

    # записываем имя и меняем стейт
    await state.update_data(location_name=location_name)
    await state.set_state(AddLocationFSM.translate_1)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)

    keyboard = await kb.cancel_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(AddLocationFSM.translate_1)
async def get_first_translate(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись первого перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_1 = message.text

    # сохраняем перевод
    await state.update_data(translation_1=translation_1)

    # меняем state
    await state.set_state(AddLocationFSM.translate_2)

    text = await t.t("add_translate", lang) + " " + await t.t(data["languages_2"], lang)
    keyboard = await kb.cancel_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_mess=msg)


@router.message(AddLocationFSM.translate_2)
async def get_second_translate(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись второго перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_2 = message.text

    # сохраняем перевод
    await state.update_data(translation_2=translation_2)

    # меняем state
    await state.set_state(AddLocationFSM.confirm)

    # получаем name
    data = await state.get_data()
    name = data["location_name"]

    text = await t.t("confirm_location", lang)
    keyboard = await kb.add_confirm_keyboard(lang)
    await message.answer(text.format(name), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "add_location_confirmed", AddLocationFSM.confirm)
async def add_location_confirm(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Запись локации"""
    lang = r.get(f"lang:{tg_id}").decode()

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    data = await state.get_data()

    # добавляем в словарь новое слово
    dictionary_for_translator = {
                lang: data['location_name'],
                data['languages_1']: data['translation_1'],
                data['languages_2']: data['translation_2']
            }
    try:
        await t.update_translation(
            dictionary_for_translator
        )
    except Exception as e:
        keyboard = await kb.cancel_keyboard(lang)
        await waiting_message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # записываем в БД
    key = await t.get_key_for_text(dictionary_for_translator["en"])
    await AsyncOrm.create_location(key, session)

    # заканчиваем стейт
    await state.clear()

    text = await t.t("new_location", lang)
    keyboard = await kb.back_and_main_menu(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "edit_location")
async def edit_location_select(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Начало изменения локации"""
    lang = r.get(f"lang:{tg_id}").decode()

    # получаем все локации
    locations = await AsyncOrm.get_locations(session)

    keyboard = await kb.edit_location_keyboard(locations, lang)
    text = await t.t("choose_location", lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_location_select")
async def edit_location_start(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Начало FSM"""
    lang = r.get(f"lang:{tg_id}").decode()
    location_id = int(callback.data.split("|")[1])
    location_old_name = callback.data.split("|")[2]

    await state.set_state(EditLocationFSM.input_name)

    # записываем id и old_name
    await state.update_data(location_id=location_id)
    await state.update_data(location_old_name=location_old_name)

    text = await t.t("set_name", lang)

    keyboard = await kb.cancel_keyboard(lang)

    msg = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(EditLocationFSM.input_name)
async def get_location_name_for_edit(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Запись имени локации"""
    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    location_name = message.text

    # записываем имя и меняем стейт
    await state.update_data(location_name=location_name)
    await state.set_state(EditLocationFSM.translate_1)

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)

    keyboard = await kb.cancel_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_mess=msg)


@router.message(EditLocationFSM.translate_1)
async def get_first_translate_for_edit(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись первого перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_1 = message.text

    # сохраняем перевод
    await state.update_data(translation_1=translation_1)

    # меняем state
    await state.set_state(EditLocationFSM.translate_2)

    text = await t.t("add_translate", lang) + " " + await t.t(data["languages_2"], lang)
    keyboard = await kb.cancel_keyboard(lang)
    msg = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_mess=msg)


@router.message(EditLocationFSM.translate_2)
async def get_second_translate(message: types.Message, tg_id: int, state: FSMContext) -> None:
    """Запись второго перевода"""
    lang = r.get(f"lang:{tg_id}").decode()

    # меняем предыдущее сообщение (убираем клавиатуру)
    data = await state.get_data()
    try:
        await data["prev_mess"].edit_text(data["prev_mess"].text)
    except Exception:
        pass

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        keyboard = await kb.cancel_keyboard(lang)
        msg = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_mess=msg)
        return

    translation_2 = message.text

    # сохраняем перевод
    await state.update_data(translation_2=translation_2)

    # меняем state
    await state.set_state(EditLocationFSM.confirm)

    # получаем name
    data = await state.get_data()
    name = data["location_name"]
    location_old_name = data["location_old_name"]

    text = await t.t("confirm_location_edit", lang)
    keyboard = await kb.edit_confirm_keyboard(lang)
    await message.answer(text.format(location_old_name, name), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "edit_location_confirmed", EditLocationFSM.confirm)
async def edit_location_confirmed(callback: types.CallbackQuery, tg_id: int, state: FSMContext, session: Any) -> None:
    """Запись локации"""
    lang = r.get(f"lang:{tg_id}").decode()

    waiting_message = await callback.message.edit_text(await t.t("please_wait", lang))

    data = await state.get_data()

    # добавляем в словарь новое слово
    dictionary_for_translator = {
                lang: data['location_name'],
                data['languages_1']: data['translation_1'],
                data['languages_2']: data['translation_2']
            }
    try:
        await t.update_translation(
            dictionary_for_translator
        )
    except Exception as e:
        keyboard = await kb.cancel_keyboard(lang)
        await waiting_message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # изменяем в БД
    key = await t.get_key_for_text(dictionary_for_translator["en"])
    await AsyncOrm.edit_location(key, data["location_id"], session)

    # заканчиваем стейт
    await state.clear()

    text = await t.t("edited_location", lang)
    keyboard = await kb.back_and_main_menu(lang)
    await waiting_message.edit_text(text, reply_markup=keyboard.as_markup())



