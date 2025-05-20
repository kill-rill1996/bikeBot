from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from routers.keyboards import menu as kb
from utils.translator import translator
from cache import r

router = Router()


# TODO test func!!!
@router.message(Command("ch_lang"))
async def change_language(message: types.Message, session: Any) -> None:
    """ТЕСТОВАЯ ФУНКЦИЯ ДЛЯ СМЕНЫ ЯЗЫКА"""
    tg_id = str(message.from_user.id)
    current_lang = r.get(f"lang:{tg_id}").decode()

    if current_lang == "ru":
        r.set(f"lang:{tg_id}", "en")
        await AsyncOrm.change_user_language(tg_id, "en", session)
        await message.answer(f"Language changed to: EN")
    elif current_lang == "en":
        r.set(f"lang:{tg_id}", "es")
        await AsyncOrm.change_user_language(tg_id, "es", session)
        await message.answer(f"Language changed to: ES")
    else:
        r.set(f"lang:{tg_id}", "ru")
        await AsyncOrm.change_user_language(tg_id, "ru", session)
        await message.answer(f"Language changed to: RU")


@router.callback_query(F.data == "main-menu")
async def show_main_menu(callback: types.CallbackQuery, admin: bool, state: FSMContext) -> None:
    """Вывод главного меню"""
    # Сброс стейта, т.к. из многих стейтов есть прямой выход в главное меню
    try:
        await state.clear()
    except Exception:
        pass

    tg_id = str(callback.from_user.id)
    user_lang = r.get(f"lang:{tg_id}").decode()
    text = translator.t("main_menu", user_lang)

    await callback.message.edit_text(text, reply_markup=kb.main_menu_keyboard(admin, user_lang).as_markup())



