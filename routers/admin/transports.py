from typing import Any

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from schemas.management import TransportCategory
from schemas.categories_and_jobs import Category
from utils.translator import translator as t, neet_to_translate_on
from database.orm import AsyncOrm

from routers.keyboards import transports as kb
from routers.states.transports import AddTransportCategoryFSM, EditCategoryFSM


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
    keyboard = await kb.cancel_keyboard(lang)
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

    keyboard = await kb.cancel_keyboard(lang)

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

    keyboard = await kb.cancel_keyboard(lang)

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
    await state.set_state()

    keyboard = await kb.to_admin_menu(lang)

    # добавляем в словарь новое слово
    try:
        await t.update_translation(
            {
                lang: data['category_name'],
                data['languages_1']: data['translation_1'],
                data['languages_2']: data['translation_2']
            }
        )
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении перевода: {e}", reply_markup=keyboard.as_markup())
        return

    # сохраняем категорию в ДБ
    category = TransportCategory(
        emoji=data["category_emoji"],
        title=data["category_name"]
    )
    try:
        await AsyncOrm.add_category(category, session)

    except Exception as e:
        await callback.message.edit_text(f"Error {e}")
        return

    text = f"✅ Категория \"{category.emoji + ' ' if category.emoji else ''}{category.title}\" успешно создана"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


# EDIT CATEGORY
@router.callback_query(F.data == "transport-management|edit_categories")
async def edit_category(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    """Начало изменений категории"""
    lang = r.get(f"lang:{tg_id}").decode()

    categories: list[Category] = await AsyncOrm.get_all_categories(session)

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


@router.callback_query(F.data.split("|")[0] == "change-category-title")
async def get_category_to_edit(callback: types.CallbackQuery, tg_id: str, session: Any, state: FSMContext) -> None:
    lang = r.get(f"lang:{tg_id}").decode()
    category_id = int(callback.data.split("|")[1])

    await state.set_state(EditCategoryFSM.input_title)

    category: Category = await AsyncOrm.get_category_by_id(category_id, session)

    text = await t.t("enter_new_title", lang)
    keyboard = await kb.back_keyboard(lang, f"edit_categories|{category.id}")

    prev_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

    await state.update_data(prev_message=prev_message)
    await state.update_data(category_id=category_id)


@router.message(EditCategoryFSM.input_title)
async def get_title_from_message(message: types.Message, tg_id: str, session: Any, state: FSMContext) -> None:
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

    new_title = message.text

    # пустой текст
    if not new_title:
        text = await t.t("wrong_text_data", lang)
        prev_message = await message.answer(text, reply_markup=keyboard.as_markup())
        await state.update_data(prev_message=prev_message)
        return

    await state.set_state(EditCategoryFSM.translate_1)



