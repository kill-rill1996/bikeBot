from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from utils.translator import translator as t
from utils.date_time_service import convert_date_time
from schemas.operations import OperationJobs


async def statistic_period_menu(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода для вывода статистики"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data="works-statistic|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data="works-statistic|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data="works-statistic|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data="works-statistic|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data="works-statistic|custom-period")
    )

    back_button: tuple = await btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def statistic_view_keyboard(lang) -> InlineKeyboardBuilder:
    """Клавиатура для просмотра меню"""
    keyboard = InlineKeyboardBuilder()

    back_button: tuple = await btn.get_back_button("works|works-statistic", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('main_menu', lang)}", callback_data="main-menu"),
    )
    return keyboard
