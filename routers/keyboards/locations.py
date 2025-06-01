from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Category
from schemas.location import Location
from schemas.search import TransportNumber, OperationJobsUserLocation
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def location_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Меню управления местоположением"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=await t.t("add_location", lang), callback_data="add_location"))
    keyboard.row(InlineKeyboardButton(text=await t.t("show_locations", lang), callback_data="show_locations"))
    keyboard.row(InlineKeyboardButton(text=await t.t("edit_location", lang), callback_data="edit_location"))

    # назад
    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def cancel_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура отмены"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=await t.t("cancel", lang), callback_data="admin|location_management"))

    return keyboard


async def add_confirm_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'✅ {await t.t("yes", lang)}', callback_data="add_location_confirmed"),
        InlineKeyboardButton(text=f'❌ {await t.t("no", lang)}', callback_data="admin|location_management")
    )

    return keyboard


async def back_and_main_menu(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура окончания записи локации"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button("admin|location_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def edit_location_keyboard(locations: List[Location], lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора локации для изменения"""
    keyboard = InlineKeyboardBuilder()

    for location in locations:
        keyboard.row(InlineKeyboardButton(text=await t.t(location.name, lang), callback_data=f"edit_location_select|{location.id}|{location.name}"))

    # назад
    back_button: tuple = await btn.get_back_button("admin|location_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def edit_confirm_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'✅ {await t.t("yes", lang)}', callback_data="edit_location_confirmed"),
        InlineKeyboardButton(text=f'❌ {await t.t("no", lang)}', callback_data="admin|location_management")
    )

    return keyboard