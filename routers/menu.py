from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from database.orm import AsyncOrm
from routers.keyboards import menu as kb

router = Router()


@router.callback_query(F.data == "main-menu")
async def show_main_menu(callback: types.CallbackQuery, admin: bool) -> None:
    """Вывод главного меню"""
    await callback.message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(admin).as_markup())



