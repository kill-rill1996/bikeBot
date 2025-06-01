from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Category
from schemas.search import TransportNumber, OperationJobsUserLocation
from utils.translator import translator as t
from utils.date_time_service import convert_date_time


async def back_keyboard(lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура назад"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def cancel_keyboard(lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура отмена"""
    keyboard = InlineKeyboardBuilder()

    # отмена
    keyboard.row(
        InlineKeyboardButton(text=await t.t("cancel", lang), callback_data=callback_data)
    )

    return keyboard


async def transport_management_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Меню раздела управление транспортом"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("add_vehicle_category", lang), callback_data="transport-management|add_category")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit_categories", lang), callback_data="transport-management|edit_categories")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("add_subcategory", lang), callback_data="transport-management|add_subcategory")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit_subcategories", lang), callback_data="transport-management|edit_subcategories")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("add_vehicle", lang), callback_data="transport-management|add_vehicle")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit_vehicle", lang), callback_data="transport-management|edit_vehicle")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("bulk_vehicle_addition", lang), callback_data="transport-management|bulk_vehicle_addition")
    )

    # назад
    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def add_emoji_keyboard(lang: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("miss_emoji", lang), callback_data="add_transport_category|skip_emoji")
    )

    # назад
    back_button: tuple = await btn.get_back_button("transport-management|add_category", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def confirm_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("yes", lang), callback_data="add-category-confirm|yes"),
        InlineKeyboardButton(text=await t.t("no", lang), callback_data="admin|vehicle_management")
    )

    return keyboard


async def confirm_keyboard_edit(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения изменения"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("yes", lang), callback_data="edit-category-confirm|yes"),
        InlineKeyboardButton(text=await t.t("no", lang), callback_data="admin|vehicle_management")
    )

    return keyboard


async def to_admin_menu(lang: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    # переход в меню менеджмента транспорта
    keyboard.row(InlineKeyboardButton(text=f"🚗 {await t.t('vehicle_management', lang)}", callback_data="admin|vehicle_management"))

    return keyboard


async def all_categories_keyboard(categories: list[Category], lang: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for category in categories:
        keyboard.row(InlineKeyboardButton(text=f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}",
                                          callback_data=f"edit_categories|{category.id}"))

    # назад
    back_button: tuple = await btn.get_back_button("admin|vehicle_management", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def edit_category(category: Category, lang: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text="Изменить название", callback_data=f"change-category-title|{category.id}"))
    keyboard.row(InlineKeyboardButton(text="Изменить эмодзи", callback_data=f"change-category-emoji|{category.id}"))

    # назад
    back_button: tuple = await btn.get_back_button("transport-management|edit_categories", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def select_category(categories: list[Category], lang: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for category in categories:
        keyboard.row(InlineKeyboardButton(
            text=f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}",
            callback_data=f"add-subcategory|{category.id}"))

    # назад
    back_button: tuple = await btn.get_back_button("admin|vehicle_management", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def confirm_add_subcategory(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения создания подкатегории"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("yes", lang), callback_data="add-subcategory-confirm|yes"),
        InlineKeyboardButton(text=await t.t("no", lang), callback_data="admin|vehicle_management")
    )

    return keyboard
