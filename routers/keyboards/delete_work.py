from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Job
from schemas.location import Location
from utils.translator import translator as t
from schemas.categories_and_jobs import Category, Subcategory, Jobtype


async def send_work_id_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура при запросе ID работы для удаления"""
    keyboard = InlineKeyboardBuilder()

    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def delete_operation_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура при просмотре работы"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=await t.t("delete_work", lang), callback_data=f"delete_operation"))

    back_button: tuple = await btn.get_back_button("admin|delete_work", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def back_to_operation(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата при вводе пароля"""
    keyboard = InlineKeyboardBuilder()

    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def confirm_delete_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Подтверждение удаления работы"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'✅ {await t.t("yes", lang)}', callback_data="delete_work_confirmed"),
        InlineKeyboardButton(text=f'❌ {await t.t("no", lang)}', callback_data="admin|delete_work")
    )

    return keyboard


async def work_deleted_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура при просмотре работы"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"admin|delete_work", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard