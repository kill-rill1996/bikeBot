from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from utils.translator import translator as t


async def works_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"➕ {await t.t('add_record', lang)}", callback_data="works|add-works"))
    keyboard.row(InlineKeyboardButton(text=f"🗂 {await t.t('my_works', lang)}", callback_data="works|my-works"))
    keyboard.row(InlineKeyboardButton(text=f"📊 {await t.t('statistic', lang)}", callback_data="works|works-statistic"))
    keyboard.row(InlineKeyboardButton(text=f"🔍 {await t.t('search_vehicle', lang)}", callback_data="works|search-vehicle"))
    keyboard.row(InlineKeyboardButton(text=f"⚙️ {await t.t('settings', lang)}", callback_data="works|settings"))

    back_button: tuple = await btn.get_back_button("main-menu", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard