from typing import Any

from aiogram import Router, types, F

from database.orm import AsyncOrm
from routers.keyboards import settings as kb
from routers.keyboards.menu import main_menu_keyboard
from utils.translator import translator as t
from cache import r

router = Router()


@router.callback_query(F.data == "menu|settings")
async def settings_menu(callback: types.CallbackQuery, tg_id: str) -> None:
    """Меню настроек пользователя"""
    lang = r.get(f"lang:{tg_id}").decode()
    text = "⚙️ " + await t.t("settings", lang)

    keyboard = await kb.settings_menu(lang)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "settings|change_language")
async def choose_language(callback: types.CallbackQuery, tg_id: str, session: Any) -> None:
    lang = r.get(f"lang:{tg_id}").decode()

    user = await AsyncOrm.get_user_by_tg_id(tg_id, session)

    text = user.username + "\n\n"

    text += "Выберите язык / Choose language / Elija idioma:"
    keyboard = await kb.choose_lang_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.split("|")[0] == "change_lang")
async def update_language(callback: types.CallbackQuery, tg_id: str, admin: bool, session: Any) -> None:
    """Изменение языка пользователя"""
    chosen_lang = callback.data.split("|")[1]

    text = "✅ " + await t.t("lang_changed", chosen_lang)
    await callback.message.edit_text(text)

    menu_text = await t.t("main_menu", chosen_lang)

    keyboard = await main_menu_keyboard(admin, chosen_lang)
    await callback.message.answer(menu_text, reply_markup=keyboard.as_markup())

    # смена языка в БД
    await AsyncOrm.change_user_language(tg_id, chosen_lang, session)

    # смена языка в кэше
    r.set(f"lang:{tg_id}", chosen_lang)
