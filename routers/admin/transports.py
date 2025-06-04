from typing import Any

from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from cache import r
from schemas.management import TransportCategory
from schemas.categories_and_jobs import Category, Subcategory
from schemas.transport import TransportSubcategory
from utils.translator import translator as t, neet_to_translate_on
from database.orm import AsyncOrm

from routers.keyboards import transports as kb
from routers.states.transports import AddTransportCategoryFSM, EditCategoryFSM, AddSubCategory, EditSubcategory, \
    AddVehicle, EditVehicle, MassiveAddVehicle
from utils.validations import parse_input_transport_numbers

router = Router()


@router.callback_query(F.data == "admin|vehicle_management")
async def reports_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню управления транспортом"""
    lang = r.get(f"lang:{tg_id}").decode()

    # Скидывем state
    try:
        await state.clear()
    except Exception as e:
        pass

    text = "🚗 " + await t.t("vehicle_management", lang)
    keyboard = await kb.transport_management_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD CATEGORY
@router.callback_query(F.data == "transport-management|add_category")
async def add_transport_category(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Добавление категории для транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()

    await state.set_state(AddTransportCategoryFSM.input_name)

    text = await t.t("enter_category_name", lang)
    keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(AddTransportCategoryFSM.input_name)
@router.callback_query(AddTransportCategoryFSM.input_emoji, F.data == "add-category|back-from-trans1")
async def get_transport_name(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Получение категории из сообщения"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # delete prev message
    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    # неверный формат названия категории
    if type(message) != types.Message:
        keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")
        text = await t.t("wrong_text_data", lang) + "\n" + await t.t("enter_category_name", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    category_name = message.text

    if not category_name:
        keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")
        text = await t.t("wrong_text_data", lang) + "\n" + await t.t("enter_category_name", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    # change state
    await state.set_state(AddTransportCategoryFSM.input_emoji)

    await state.update_data(category_name=category_name)

    text = await t.t("category_emoji", lang)
    keyboard = await kb.add_emoji_keyboard(lang)
    prev_message = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


@router.callback_query(AddTransportCategoryFSM.input_emoji, F.data.split("add_transport_category|skip_emoji"))
@router.message(AddTransportCategoryFSM.input_emoji)
async def get_transport_emoji(message: types.Message | types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Получаем эмодзи"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # получаем языки на которые нужно перевести
    languages: list[str] = await neet_to_translate_on(lang)

    # формируем клавиатуру и сообщение для ответа
    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")
    text = await t.t("add_translate", lang) + " " + await t.t(languages[0], lang)

    # сохраняем требуемые языки в data
    await state.update_data(languages_1=languages[0])
    await state.update_data(languages_2=languages[1])

    # при пропуске эмодзи
    if type(message) == types.CallbackQuery:
        await state.update_data(category_emoji=None)
        prev_message = await message.message.edit_text(text, reply_markup=keyboard.as_markup())

    # types.Message
    else:
        # delete prev message
        try:
            await data["prev_message"].delete()
        except Exception:
            pass

        category_emoji = message.text

        if not category_emoji:
            keyboard = await kb.add_emoji_keyboard(lang)
            text = await t.t("category_emoji", lang)
            prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

        await state.update_data(category_emoji=category_emoji)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())

    # save message to delete
    await state.update_data(prev_message=prev_message)
    # change state
    await state.set_state(AddTransportCategoryFSM.translate_1)


@router.message(AddTransportCategoryFSM.translate_1)
async def get_first_translation(message: types.Message, state: FSMContext, tg_id: str) -> None:
    """Принимаем перевод на первом языке"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # delete prev message
    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    translation_1 = message.text

    # пустой текст
    if not translation_1:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    # сохраняем перевод
    await state.update_data(translation_1=translation_1)

    # меняем state
    await state.set_state(AddTransportCategoryFSM.translate_2)

    text = await t.t("add_translate", lang) + " " + await t.t(data["languages_2"], lang)
    prev_message = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


@router.message(AddTransportCategoryFSM.translate_2)
async def get_second_translation(message: types.Message, state: FSMContext, tg_id: str) -> None:
    """Получаем второй перевод"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()

    # delete prev message
    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    translation_2 = message.text

    # пустой текст
    if not translation_2:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

        # сохраняем перевод
    await state.update_data(translation_2=translation_2)

    # меняем state
    await state.set_state(AddTransportCategoryFSM.confirm)

    data = await state.get_data()

    # если добавляли эмоджи
    if data["category_emoji"]:
        # формируем превью
        text = f"{await t.t('add_a_category', lang)} \"{data['category_emoji']} {data['category_name']}\"\n"

    # без эмоджи
    else:
        text = f"{await t.t('add_a_category', lang)} \"{data['category_name']}\"\n"

    # добавляем переводы
    text += f"{await t.t(data['languages_1'], lang)}: \"{data['category_emoji'] + ' ' if data['category_emoji'] else ''}{data['translation_1']}\"\n"
    text += f"{await t.t(data['languages_2'], lang)}: \"{data['category_emoji'] + ' ' if data['category_emoji'] else ''}{data['translation_2']}\"\n"

    confirm_keyboard = await kb.confirm_keyboard(lang)

    await message.answer(text, reply_markup=confirm_keyboard.as_markup())


@router.callback_query(AddTransportCategoryFSM.confirm, F.data.split("|")[0] == "add-category-confirm")
async def save_category(callback: types.CallbackQuery, state: FSMContext, tg_id: str, session: Any) -> None:
    """Конец FSM, сохранение категории"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()
    # await state.set_state()

    keyboard = await kb.to_admin_menu(lang)

    new_words_for_translator = {
                lang: data['category_name'],
                data['languages_1']: data['translation_1'],
                data['languages_2']: data['translation_2']
            }
    # добавляем в словарь новое слово
    try:
        await t.update_translation(
            new_words_for_translator
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # формируем ключ сохранения в БД
    category_name_for_db = await t.get_key_for_text(new_words_for_translator['en'])
    # сохраняем категорию в ДБ
    category = TransportCategory(
        emoji=data['category_emoji'],
        title=category_name_for_db
    )
    try:
        await AsyncOrm.add_category(category, session)

    except Exception as e:
        await callback.message.edit_text(f"Error {e}")
        return

    text = f"✅ Категория \"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}\" успешно создана"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# EDIT CATEGORY
@router.callback_query(F.data == "transport-management|edit_categories")
async def edit_category(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Начало изменений категории"""
    lang = r.get(f"lang:{tg_id}").decode()

    categories: list[Category] = await AsyncOrm.get_all_categories(session)
    if not categories:
        keyboard = await kb.there_are_not_yet("admin|vehicle_management", lang)
        await callback.message.edit_text("у вас пока нет категорий", reply_markup=keyboard.as_markup())
        return

    text = await t.t("select_category_to_edit", lang)
    keyboard = await kb.all_categories_keyboard(categories, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit_categories")
async def get_category_to_edit(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Вывод выбранный категории"""
    try:
        await state.clear()
    except Exception as e:
        pass

    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    category: Category = await AsyncOrm.get_category_by_id(category_id, session)

    keyboard = await kb.edit_category(category, lang)
    text = f"{await t.t('category', lang)} \"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}\""

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# EDIT CATEGORY TITLE
@router.callback_query(F.data.split("|")[0] == "change-category-title")
async def get_category_to_edit(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(EditCategoryFSM.input_title)

    category: Category = await AsyncOrm.get_category_by_id(category_id, session)

    # для удаления ключевого слова в дальнейшем
    await state.update_data(old_category=category)

    text = await t.t("enter_new_title", lang)
    keyboard = await kb.back_keyboard(lang, f"edit_categories|{category.id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)
    await state.update_data(category_id=category_id)


@router.message(EditCategoryFSM.input_title)
async def get_title_from_message(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Получаем новое название из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    keyboard = await kb.back_keyboard(lang, f"edit_categories|{data['category_id']}")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    category_name = message.text

    # пустой текст
    if not category_name:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditCategoryFSM.translate_1)

    # получаем языки на которые нужно перевести
    neet_to_translate = await neet_to_translate_on(lang)

    await state.update_data(languages_1=neet_to_translate[0])
    await state.update_data(languages_2=neet_to_translate[1])
    await state.update_data(category_name=category_name)

    text = await t.t("add_translate", lang) + " " + await t.t(neet_to_translate[0], lang)
    prev_message = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


@router.message(EditCategoryFSM.translate_1)
async def get_translate_1(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Получаем первый перевод"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()

    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, f"edit_categories|{data['category_id']}")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    translation_1 = message.text

    # пустой текст
    if not translation_1:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditCategoryFSM.translate_2)

    await state.update_data(translation_1=translation_1)

    text = await t.t("add_translate", lang) + " " + await t.t(data['languages_2'], lang)
    prev_message = await message.answer(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)


@router.message(EditCategoryFSM.translate_2)
async def get_translate_2(message: types.Message, tg_id: str, state: FSMContext) -> None:
    """Получаем второй перевод, предлагаем сохранить"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()

    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, f"edit_categories|{data['category_id']}")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    translation_2 = message.text

    # пустой текст
    if not translation_2:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditCategoryFSM.confirm)

    await state.update_data(translation_2=translation_2)

    text = f"{await t.t('save_changes', lang)}? \"{data['category_name']}\"\n"
    # добавляем переводы
    text += f"{await t.t(data['languages_1'], lang)}: \"{data['translation_1']}\"\n"
    text += f"{await t.t(data['languages_2'], lang)}: \"{translation_2}\"\n"

    confirm_keyboard = await kb.confirm_keyboard(lang)

    await message.answer(text, reply_markup=confirm_keyboard.as_markup())


@router.callback_query(EditCategoryFSM.confirm, F.data.split("|")[0] != "edit-category-confirm")
async def confirm_changes(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Сохраняем изменения"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()
    await state.clear()

    keyboard = await kb.to_admin_menu(lang)

    # удаляем старое ключевое слово
    try:
        old_category: Category = data["old_category"]
        keyword = await t.get_key_for_text(old_category.title)

        await t.delete_key_word(keyword)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении измененного перевода: {e}",
                                         reply_markup=keyboard.as_markup())
        return

    # добавляем в словарь новое слово
    words_for_translator = {
                lang: data['category_name'],
                data['languages_1']: data['translation_1'],
                data['languages_2']: data['translation_2']
            }
    try:
        await t.update_translation(
            words_for_translator
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    try:
        # save to DB
        await AsyncOrm.update_category_title(
            category_id=int(data['category_id']),
            title=await t.get_key_for_text(words_for_translator['en']),
            session=session
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при внесении изменений: {e}")
        return

    text = f"✅ Категория {data['category_name']} успешно изменена"
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# CHANGE CATEGORY EMOJI
@router.callback_query(F.data.split("|")[0] == "change-category-emoji")
async def change_emoji_for_category(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Изменение эмодзи у категории"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = callback.data.split("|")[1]

    await state.set_state(EditCategoryFSM.input_emoji)

    await state.update_data(category_id=category_id)

    text = await t.t("category_emoji", lang)
    keyboard = await kb.back_keyboard(lang, f"edit_categories|{category_id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await state.update_data(prev_message=prev_message)


@router.message(EditCategoryFSM.input_emoji)
async def get_emoji_from_text(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получаем эмодзи из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    try:
        await data["prev_message"].delete()
    except Exception:
        pass

    category_emoji = message.text

    if not category_emoji:
        keyboard = await kb.cancel_keyboard(lang, f"edit_categories|{data['category_id']}")
        text = await t.t("category_emoji", lang)

        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditCategoryFSM.confirm)
    await state.update_data(category_emoji=category_emoji)

    category: Category = await AsyncOrm.get_category_by_id(int(data['category_id']), session)

    text = await t.t("save_changes", lang) + "?\n"
    text += f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)} -> "
    text += f"{category_emoji} {await t.t(category.title, lang)}"

    keyboard = await kb.confirm_keyboard_edit(lang)

    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit-category-confirm", EditCategoryFSM.confirm)
async def save_emoji_changing(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Сохранение измененного эмодзи"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    await state.clear()
    keyboard = await kb.to_admin_menu(lang)
    category: Category = await AsyncOrm.get_category_by_id(int(data['category_id']), session)

    try:
        await AsyncOrm.update_category_emoji(int(data['category_id']), data['category_emoji'], session)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при внесении изменений: {e}", reply_markup=keyboard.as_markup())
        return

    text = f"✅ Категория \"{data['category_emoji']} {await t.t(category.title, lang)}\" успешно изменена"
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD SUBCATEGORY
@router.callback_query(F.data == "transport-management|add_subcategory")
async def add_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Добавление подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()

    try:
        await state.clear()
    except Exception:
        pass

    categories: list[Category] = await AsyncOrm.get_all_categories(session)

    # если пока нет категорий
    if not categories:
        keyboard = await kb.there_are_not_yet("admin|vehicle_management", lang)
        await callback.message.edit_text("у вас пока нет категорий", reply_markup=keyboard.as_markup())
        return

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category(categories, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "add-subcategory")
async def selected_category(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Добавление подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(AddSubCategory.input_subcategory)

    # get from DB
    category: Category = await AsyncOrm.get_category_by_id(category_id, session)
    subcategories: list[Subcategory] = await AsyncOrm.get_subcategories_by_category(category_id, session)

    # generate message
    text = await t.t("existing_subcategories", lang) + " \n"
    text += f"\"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}\"\n"
    # если уже есть категории
    if subcategories:
        for subcategory in subcategories:
            text += f"\t\t• {subcategory.title}\n"
    else:
        text += f"В этой категории пока еще нет подкатегорий\n"
    text += "\n"
    text += await t.t("enter_new_sub_category", lang)

    keyboard = await kb.back_keyboard(lang, "transport-management|add_subcategory")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    # save data
    await state.update_data(category_id=category_id)
    await state.update_data(category_title=category.title)
    await state.update_data(category_emoji=category.emoji)
    await state.update_data(prev_message=prev_message)


@router.message(AddSubCategory.input_subcategory)
async def get_subcategory_from_text(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получение подкатегории из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    prev_message = data["prev_message"]
    category_id = int(data["category_id"])
    category_title = data["category_title"]
    category_emoji = data["category_emoji"]

    try:
        await prev_message.delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, f"transport-management|add_subcategory")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    new_subcategory = message.text

    # пустой текст
    if not new_subcategory:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    # проверяем существует ли уже такая подкатегория
    subcategories: list[Subcategory] = await AsyncOrm.get_subcategories_by_category(category_id, session)
    for subcategory in subcategories:
        if subcategory.title == new_subcategory:
            await message.answer(await t.t("subcategory_already_exists", lang), reply_markup=keyboard.as_markup())
            return

    await state.update_data(new_subcategory=new_subcategory)
    await state.set_state(AddSubCategory.confirm)

    text = await t.t("save_subcategory", lang) + "\n"
    text += f"{category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> {new_subcategory}"

    keyboard = await kb.confirm_add_subcategory(lang)

    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "add-subcategory-confirm|yes", AddSubCategory.confirm)
async def save_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    category_id = int(data["category_id"])
    subcategory_title = data["new_subcategory"]
    category_title = data["category_title"]

    await state.clear()

    keyboard = await kb.to_admin_menu(lang)

    # save to DB
    try:
        await AsyncOrm.create_subcategory(category_id, subcategory_title, session)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении подкатегории: {e}", reply_markup=keyboard.as_markup())
        return

    text = f"✅ Подкатегория \"{subcategory_title}\" для категории {await t.t(category_title, lang)} успешно создана"
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# EDIT SUBCATEGORIES
@router.callback_query(F.data == "transport-management|edit_subcategories")
async def edit_subcategory(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Изменение подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()

    try:
        await state.clear()
    except Exception:
        pass

    categories: list[Category] = await AsyncOrm.get_all_categories(session)

    # если пока нет категорий
    if not categories:
        keyboard = await kb.there_are_not_yet("admin|vehicle_management", lang)
        await callback.message.edit_text("у вас пока нет категорий", reply_markup=keyboard.as_markup())
        return

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category_edit_subcategory(categories, lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "edit-subcategory")
async def selected_category_to_edit(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    """Изменение подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(EditSubcategory.input_category)

    # get from DB
    category: Category = await AsyncOrm.get_category_by_id(category_id, session)
    subcategories: list[Subcategory] = await AsyncOrm.get_subcategories_by_category(category_id, session)

    # generate message
    text = f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}\n"
    text += await t.t("select_subcategory_to_edit", lang)

    keyboard = await kb.subcategories_for_category(subcategories, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    # save data
    await state.update_data(category_id=category_id)
    await state.update_data(category_title=category.title)
    await state.update_data(category_emoji=category.emoji)


@router.callback_query(F.data.split("|")[0] == "subcategory-to-edit")
async def get_subcategory_to_edit(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Получаем выбранную подкатегорию"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    category_id = data['category_id']
    subcategory_id = int(callback.data.split("|")[1])

    await state.set_state(EditSubcategory.input_subcategory)

    text = f"{await t.t('enter_new_subcategory_name', lang)}"
    keyboard = await kb.back_keyboard(lang, f"edit-subcategory|{category_id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(subcategory_id=subcategory_id)
    await state.update_data(prev_message=prev_message)


@router.message(EditSubcategory.input_subcategory)
async def get_subcategory_title_from_text(message: types.Message, tg_id: str, session: Any, state: FSMContext) -> None:
    """Получаем новое название подкатегории из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    prev_message = data["prev_message"]
    category_id = data["category_id"]
    category_title = data["category_title"]
    category_emoji = data["category_emoji"]

    try:
        await prev_message.delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    subcategory_title = message.text

    # пустой текст
    if not subcategory_title:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    # проверяем что такой подкатегории еще нет
    subcategories: list[Subcategory] = await AsyncOrm.get_subcategories_by_category(category_id, session)
    if subcategory_title in [subcategory.title for subcategory in subcategories]:
        text = f"В категории {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} " \
               f"уже существует подкатегория {subcategory_title}\n" \
               f"Введите другое название"
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditSubcategory.confirm)
    await state.update_data(subcategory_title=subcategory_title)

    text = await t.t("save_changes", lang) + "?\n"
    text += f"{category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> {subcategory_title}"

    keyboard = await kb.confirm_edit_subcategory(lang)

    await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "edit-subcategory-confirm|yes", EditSubcategory.confirm)
async def save_edited_subcategory(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Сохранение измененной подкатегории"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    category_title = data["category_title"]
    subcategory_id = data["subcategory_id"]
    subcategory_title = data["subcategory_title"]

    await state.clear()
    keyboard = await kb.to_admin_menu(lang)

    # change in DB
    try:
        await AsyncOrm.update_subcategory(subcategory_id, subcategory_title, session)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при изменении подкатегории: {e}", reply_markup=keyboard.as_markup())
        return

    text = f"✅ Подкатегория \"{subcategory_title}\" для категории {await t.t(category_title, lang)} успешно создана"
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# ADD VEHICLE / EDIT VEHICLE / MASSIVE ADDING
@router.callback_query(or_f(
    F.data == "transport-management|add_vehicle",
    F.data == "transport-management|edit_vehicle",
    F.data == "transport-management|bulk_vehicle_addition"
    )
)
async def add_vehicle(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Выбор операции с транспортом"""
    lang = r.get(f"lang:{tg_id}").decode()

    categories: list[Category] = await AsyncOrm.get_all_categories(session)

    # for add
    if callback.data == "transport-management|add_vehicle":
        await state.set_state(AddVehicle.input_category)
    # for update
    elif callback.data == "transport-management|edit_vehicle":
        await state.set_state(EditVehicle.input_category)
    # for mass adding
    elif callback.data == "transport-management|bulk_vehicle_addition":
        await state.set_state(MassiveAddVehicle.input_category)

    # если пока нет категорий
    if not categories:
        keyboard = await kb.there_are_not_yet("admin|vehicle_management", lang)
        await callback.message.edit_text("у вас пока нет категорий", reply_markup=keyboard.as_markup())
        return

    text = await t.t("select_category", lang)
    keyboard = await kb.select_category_add_transport(categories, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(or_f(AddVehicle.input_category, EditVehicle.input_category, MassiveAddVehicle.input_category, F.data.split("|")[0] == "admin-add-transport"))
async def select_category_for_add_vehicle(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Выбор категории транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])
    current_state = await state.get_state()

    # change state
    if current_state in (AddVehicle.input_category, AddVehicle.input_vehicle):
        await state.set_state(AddVehicle.input_subcategory)
    elif current_state in (EditVehicle.input_category, EditVehicle.input_vehicle):
        await state.set_state(EditVehicle.input_subcategory)
    elif current_state in (MassiveAddVehicle.input_category, MassiveAddVehicle.input_vehicle):
        await state.set_state(MassiveAddVehicle.input_subcategory)

    # from DB
    category: Category = await AsyncOrm.get_category_by_id(category_id, session)
    subcategories: list[Subcategory] = await AsyncOrm.get_subcategories_by_category(category_id, session)

    # если пока нет подкатегорий
    if not subcategories:
        keyboard = await kb.there_are_not_yet("admin|vehicle_management", lang)
        await callback.message.edit_text("у вас пока нет подкатегорий", reply_markup=keyboard.as_markup())
        return

    text = f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}\n"
    text += await t.t("select_subcategory", lang)

    keyboard = await kb.subcategories_for_add_vehicle(subcategories, lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(category_id=category_id)
    await state.update_data(category_title=category.title)
    await state.update_data(category_emoji=category.emoji)


@router.callback_query(or_f(AddVehicle.input_subcategory, EditVehicle.input_subcategory, MassiveAddVehicle.input_subcategory))
async def select_subcategory(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Отлавливаем подкатегорию"""
    lang = r.get(f"lang:{tg_id}").decode()
    subcategory_id = int(callback.data.split("|")[1])
    current_state = await state.get_state()

    data = await state.get_data()
    category_emoji = data["category_emoji"]
    category_title = data["category_title"]
    category_id = data["category_id"]

    # from DB
    subcategory: Subcategory = await AsyncOrm.get_subcategory_by_id(subcategory_id, session)

    # change state
    if current_state == AddVehicle.input_subcategory:
        await state.set_state(AddVehicle.input_vehicle)
    elif current_state == EditVehicle.input_subcategory:
        await state.set_state(EditVehicle.input_vehicle)
    elif current_state == MassiveAddVehicle.input_subcategory:
        await state.set_state(MassiveAddVehicle.input_vehicle)

    text = f"{category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> {subcategory.title}\n"
    if current_state == MassiveAddVehicle.input_subcategory:
        text += await t.t("input_transport_number_massive", lang)
    else:
        text += await t.t("input_transport_number", lang)

    keyboard = await kb.back_keyboard(lang, f"admin-add-transport|{category_id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(subcategory_id=subcategory_id)
    await state.update_data(subcategory_title=subcategory.title)
    await state.update_data(prev_message=prev_message)


@router.message(or_f(AddVehicle.input_vehicle, EditVehicle.input_vehicle, MassiveAddVehicle.input_vehicle))
async def input_transport_number(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получаем номер транспорта из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    # get data from state
    prev_message = data["prev_message"]
    subcategory_id = int(data["subcategory_id"])
    category_emoji = data["category_emoji"]
    category_title = data["category_title"]
    subcategory_title = data["subcategory_title"]

    try:
        await prev_message.delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    input_text = message.text

    # FOR ADD / FOR EDIT
    if current_state == AddVehicle.input_vehicle or current_state == EditVehicle.input_vehicle:
    # пустой текст или не цифра
        if not input_text or not input_text.isdigit():
            text = await t.t("wrong_text_data", lang)
            prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

    # FOR ADD
    if current_state == AddVehicle.input_vehicle:

        # проверяем что такого транспорта еще нет
        transports: list[TransportSubcategory] = await AsyncOrm.get_transports_for_subcategory(subcategory_id, session)
        if int(input_text) in [transport.serial_number for transport in transports]:
            text = f"В категории {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> " \
                   f"{subcategory_title} уже существует транспорт с серийным номером {input_text}\n" \
                   f"Введите другое число"
            prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

        # Если все нормально и такого номера транспорта еще нет
        await state.set_state(AddVehicle.confirm)

        text = f"Добавить транспорт?\n{category_emoji + ' ' if category_emoji else ''}{category_title} -> {subcategory_title}-{input_text}"
        keyboard = await kb.confirm_transport_create_keyboard(lang)
        await message.answer(text, reply_markup=keyboard.as_markup())

    # FOR UPDATE
    elif current_state == EditVehicle.input_vehicle:
        try:
            transport = await AsyncOrm.get_transport_by_number_and_subcategory(int(input_text), subcategory_id, session)
            # если такой транспорт не найден
            if not transport:
                text = f"В категории {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> " \
                       f"{subcategory_title} не существует транспорта с серийным номером {input_text}\n" \
                       f"Введите другое число"
                prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
                await state.update_data(prev_message=prev_message)
                return

        # Ошибка в DB
        except Exception as e:
            text = f"Ошибка при получении транспорта {e}"
            prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

        # EDIT VEHICLE
        await state.set_state(EditVehicle.input_new_vehicle)

        text = f"Введите новый номер транспорта:\n(например, \"22\")"
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)

    # FOR MASSIVE ADDING
    elif current_state == MassiveAddVehicle.input_vehicle:
        try:
            numbers_list = parse_input_transport_numbers(input_text)

            # проверяем существует ли уже такой транспорт
            already_exists = []
            transports: [TransportSubcategory] = await AsyncOrm.get_transports_for_subcategory(subcategory_id, session)
            serial_numbers_list = [transport.serial_number for transport in transports]

            for num in numbers_list:
                if num in serial_numbers_list:
                    already_exists.append(num)

            # если все норм и такого транспорта еще нет
            if not already_exists:
                await state.update_data(numbers_list=numbers_list)
                await state.update_data(numbers_string=input_text)
                await state.set_state(MassiveAddVehicle.confirm)

                text = f"Добавить {len(numbers_list)} единиц транспорта \"{input_text}\" в категорию {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} подкатегорию {subcategory_title}?"
                keyboard = await kb.confirm_transport_create_keyboard(lang)
                await message.answer(text, reply_markup=keyboard.as_markup())

            # если уже существует транспорт
            else:
                text = f"Транспорт с номерами "
                for num in already_exists:
                    text += f"{num}, "

                text = text[:-2] + f" в категории {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} уже существует\nВведите другие значения"
                prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
                await state.update_data(prev_message=prev_message)
                return

        except Exception:
            text = await t.t("wrong_text_data", lang)
            prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
            await state.update_data(prev_message=prev_message)
            return

    # save to state
    await state.update_data(transport_number=input_text)


@router.message(EditVehicle.input_new_vehicle)
async def get_new_serial_number_from_text(message: types.Message, tg_id: str, state: FSMContext, session: Any) -> None:
    """Получаем новый номер транспорта из текста"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()

    # get data from state
    prev_message = data["prev_message"]
    subcategory_id = int(data["subcategory_id"])
    category_emoji = data["category_emoji"]
    category_title = data["category_title"]
    subcategory_title = data["subcategory_title"]
    old_transport_number = data["transport_number"]

    try:
        await prev_message.delete()
    except Exception:
        pass

    keyboard = await kb.cancel_keyboard(lang, "admin|vehicle_management")

    # неверный формат
    if type(message) != types.Message:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    new_transport_number = message.text

    # пустой текст или не цифра
    if not new_transport_number or not new_transport_number.isdigit():
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    # проверяем что такого транспорта еще нет
    transports: list[TransportSubcategory] = await AsyncOrm.get_transports_for_subcategory(subcategory_id, session)
    if int(new_transport_number) in [transport.serial_number for transport in transports]:
        text = f"В категории {category_emoji + ' ' if category_emoji else ''}{await t.t(category_title, lang)} -> " \
               f"{subcategory_title} уже существует транспорт с серийным номером {new_transport_number}\n" \
               f"Введите другое число"
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditVehicle.confirm)

    # TODO make translation
    # text = await t.t("")

    text = f"Сохранить изменения транспорта?\n{subcategory_title}-{old_transport_number} -> {subcategory_title}-{new_transport_number}"
    keyboard = await kb.confirm_transport_create_keyboard(lang)
    await message.answer(text, reply_markup=keyboard.as_markup())

    # save to state
    await state.update_data(new_transport_number=new_transport_number)


@router.callback_query(or_f(AddVehicle.confirm, EditVehicle.confirm, MassiveAddVehicle.confirm))
async def confirm_transport_add(callback: types.CallbackQuery, tg_id: str, state: FSMContext, session: Any) -> None:
    """Подтверждение создания транспорта"""
    lang = r.get(f"lang:{tg_id}").decode()
    data = await state.get_data()
    current_state = await state.get_state()

    subcategory_id = int(data["subcategory_id"])
    category_emoji = data["category_emoji"]
    category_title = data["category_title"]
    category_id = int(data["category_id"])
    subcategory_title = data["subcategory_title"]

    await state.clear()
    keyboard = await kb.to_admin_menu(lang)

    # save to DB
    # FOR ADD
    if current_state == AddVehicle.confirm:
        serial_number = int(data["transport_number"])
        try:
            await AsyncOrm.create_transport(serial_number, subcategory_id, category_id, session)
            text = f"✅ Транспорт {category_emoji + ' ' if category_emoji else ''}{category_title} -> {subcategory_title}-{serial_number} успешно создан"
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при создании транспорта: {e}", reply_markup=keyboard.as_markup())
            return
    # FOR EDIT
    elif current_state == EditVehicle.confirm:
        serial_number = int(data["transport_number"])
        try:
            new_transport_number = int(data["new_transport_number"])
            await AsyncOrm.edit_transport(new_transport_number, serial_number, subcategory_id, session)
            text = f"✅ Транспорт {category_emoji + ' ' if category_emoji else ''}{category_title} -> {subcategory_title}-{new_transport_number} успешно изменен"
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при изменении транспорта: {e}", reply_markup=keyboard.as_markup())
            return

    # FOR MASSIVE ADDING
    elif current_state == MassiveAddVehicle.confirm:
        numbers_list = data["numbers_list"]
        numbers_string = data["numbers_string"]

        try:
            for transport_number in numbers_list:
                await AsyncOrm.create_transport(int(transport_number), subcategory_id, category_id, session)

            text = f"✅ Транспорт {category_emoji + ' ' if category_emoji else ''}{category_title} -> {subcategory_title} {numbers_string} успешно создан"

        except Exception as e:
            await callback.message.edit_text(f"Ошибка при создании транспорта: {e}", reply_markup=keyboard.as_markup())
            return

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())











