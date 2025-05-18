from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from database.orm import AsyncOrm
from routers.keyboards import menu as kb
from utils.translator import translator
from cache import r

router = Router()


@router.callback_query(F.data == "main-menu")
async def show_main_menu(callback: types.CallbackQuery, admin: bool) -> None:
    """Вывод главного меню"""
    tg_id = str(callback.from_user.id)
    user_lang = r.get(f"lang:{tg_id}")
    text = translator.t("main_menu", user_lang)

    await callback.message.edit_text(text, reply_markup=kb.main_menu_keyboard(admin).as_markup())



