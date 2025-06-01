from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Category
from schemas.location import Location
from schemas.search import TransportNumber, OperationJobsUserLocation
from schemas.users import User
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def users_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Меню управления пользователями"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=await t.t("add_user", lang), callback_data="add_user"))
    keyboard.row(InlineKeyboardButton(text=await t.t("show_user", lang), callback_data="show_user"))

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

    # назад
    back_button: tuple = await btn.get_back_button("admin|user_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def choose_user_role(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора роли"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("mechanic", lang), callback_data="role|mechanic"),
        InlineKeyboardButton(text=await t.t("admin", lang), callback_data="role|admin")
    )

    # назад
    back_button: tuple = await btn.get_back_button("admin|user_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def confirm_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения создания пользователя"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'✅ {await t.t("yes", lang)}', callback_data="add_user_confirmed"),
        InlineKeyboardButton(text=f'❌ {await t.t("no", lang)}', callback_data="admin|user_management")
    )

    return keyboard


async def back_and_main_menu(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура назад и главное меню"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button("admin|user_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def users_keyboard(users: List[User], lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для выбора пользователей"""
    keyboard = InlineKeyboardBuilder()

    for user in users:
        keyboard.row(InlineKeyboardButton(text=user.username, callback_data=f"show_user_choose|{user.id}"))
    keyboard.adjust(2)

    # назад
    back_button: tuple = await btn.get_back_button("admin|user_management", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def user_detail_keyboard(user: User, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура просмотра пользователя"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=await t.t("edit_user", lang), callback_data=f"edit_user|{user.id}"))
    keyboard.row(InlineKeyboardButton(text=await t.t("delete_user", lang), callback_data=f"delete_user|{user.id}"))

    # назад
    back_button: tuple = await btn.get_back_button("show_user", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def delete_confirm_keyboard(user_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения удаления пользователей"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'✅ {await t.t("yes", lang)}', callback_data=f"delete_user_confirmed|{user_id}"),
        InlineKeyboardButton(text=f'❌ {await t.t("no", lang)}', callback_data=f"show_user_choose|{user_id}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"show_user_choose|{user_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard