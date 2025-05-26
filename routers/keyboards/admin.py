from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.users import User
from utils.translator import translator as t


async def admin_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📑 {await t.t('reports', lang)}", callback_data="admin|reports"))
    keyboard.row(InlineKeyboardButton(text=f"🚗 {await t.t('vehicle_management', lang)}", callback_data="admin|vehicle_management"))
    keyboard.row(InlineKeyboardButton(text=f"🌎 {await t.t('location_management', lang)}", callback_data="admin|location_management"))
    keyboard.row(InlineKeyboardButton(text=f"🛠 {await t.t('operation_management', lang)}", callback_data="admin|operation_management"))
    keyboard.row(InlineKeyboardButton(text=f"👤 {await t.t('user_management', lang)}", callback_data="admin|user_management"))

    back_button: tuple = await btn.get_back_button("main-menu", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def reports_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню отчетов администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('individual_mechanic_report', lang)}", callback_data="admin-reports|individual_mechanic_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('summary_report_by_mechanics', lang)}", callback_data="admin-reports|summary_report_by_mechanics"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('vehicle_report', lang)}", callback_data="admin-reports|vehicle_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('work_categories_report', lang)}", callback_data="admin-reports|work_categories_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('inefficiency_report', lang)}", callback_data="admin-reports|inefficiency_report"))

    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_period_keyboard(report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода отчета"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data=f"reports-period|{report_type}|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data=f"reports-period|{report_type}|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data=f"reports-period|{report_type}|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data=f"reports-period|{report_type}|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data=f"reports-period|{report_type}|custom-period")
    )

    # назад
    back_button: tuple = await btn.get_back_button("admin|reports", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))
    return keyboard


async def choose_mechanic(mechanics: List[User], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора механика"""
    keyboard = InlineKeyboardBuilder()

    for mechanic in mechanics:
        keyboard.row(InlineKeyboardButton(text=mechanic.username, callback_data=f"mechanic|{period}|{mechanic.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard