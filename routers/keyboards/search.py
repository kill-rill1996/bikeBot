from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
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


async def transport_jobs_keyboard(lang: str, transports: list[TransportNumber]) -> InlineKeyboardBuilder:
    """Клавиатура вывода найденных транспортов и работ"""
    keyboard = InlineKeyboardBuilder()

    # кнопки с транспортом
    for transport in transports:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{transport.subcategory_title}-{transport.serial_number}",
                callback_data=f"searched_transport|{transport.id}"
            )
        )
    keyboard.adjust(3)

    # назад
    back_button: tuple = await btn.get_back_button("works|search-vehicle", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def transport_period_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода для вывода моих работ"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data="search_period|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data="search_period|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data="search_period|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data="search_period|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data="search_period|custom-period")
    )

    back_button: tuple = await btn.get_back_button("back_from_search_result", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def found_operations_keyboard(
        operations: [OperationJobsUserLocation], lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура назад"""
    keyboard = InlineKeyboardBuilder()

    # формируем из операций кнопки в формате date: ID|category|subcat-sn
    for operation in operations:
        date = convert_date_time(operation.created_at, True)[0]
        text = f"{date}: {operation.id} | {await t.t(operation.category_title, lang)} | " \
               f"{operation.subcategory_title}-{operation.serial_number}"
        keyboard.row(
            InlineKeyboardButton(text=text, callback_data=f"operation-detail|{operation.id}"),
        )

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def back_and_main_menu_keyboard(callback_data: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура в главное меню и назад"""

    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    # кнопка главное меню
    keyboard.row(
        InlineKeyboardButton(text=await t.t("main_menu", lang), callback_data="main-menu")
    )

    return keyboard

    return keyboard