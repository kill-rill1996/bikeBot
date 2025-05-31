from typing import Any

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from cache import r
from schemas.management import TransportCategory
from utils.translator import translator as t
from database.orm import AsyncOrm

from routers.keyboards import transports as kb
from routers.states.transports import AddTransportCategoryFSM

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
        print("ЗАЩИТА 1")
        keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")
        text = await t.t("wrong_text_data", lang) + "\n" + await t.t("enter_category_name", lang)
        await message.answer(text, reply_markup=keyboard.as_markup())
        return

    category_name = message.text

    if not category_name:
        print("ЗАЩИТА 2")
        keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")
        text = await t.t("wrong_text_data", lang) + "\n" + await t.t("enter_category_name", lang)
        await message.answer(text, reply_markup=keyboard.as_markup())
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

    keyboard = await kb.confirm_keyboard(lang)

    # при пропуске эмодзи
    if type(message) == types.CallbackQuery:

        await state.set_state(AddTransportCategoryFSM.confirm)
        await state.update_data(category_emoji=None)

        text = f"Add category? \"{data['category_name']}\""
        await message.message.edit_text(text, reply_markup=keyboard.as_markup())

    # types.Message
    else:
        # delete prev message
        try:
            await data["prev_message"].delete()
        except Exception:
            pass

        category_emoji = message.text

        if not category_emoji:
            keyboard = await kb.back_keyboard(lang, "admin|vehicle_management")
            text = await t.t("category_emoji", lang) + "\n" + await t.t("enter_category_name", lang)
            await message.answer(text, reply_markup=keyboard.as_markup())
            return

        await state.set_state(AddTransportCategoryFSM.confirm)
        await state.update_data(category_emoji=category_emoji)

        text = f"Add category? \"{category_emoji} {data['category_name']}\""
        await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(AddTransportCategoryFSM.confirm, F.data.split("|")[0] == "add-category-confirm")
async def save_category(callback: types.CallbackQuery, state: FSMContext, tg_id: str, session: Any) -> None:
    """Конец FSM, сохранение категории"""
    lang = r.get(f"lang:{tg_id}").decode()

    data = await state.get_data()

    category = TransportCategory(
        emoji=data["category_emoji"],
        title=data["category_name"]
    )
    try:
        await AsyncOrm.add_category(category, session)

    except Exception as e:
        await callback.message.edit_text(f"Error {e}")
        return

    text = "✅ Категория успешно создана"
    keyboard = await kb.to_admin_menu(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


