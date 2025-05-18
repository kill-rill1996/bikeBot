from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard(admin: bool) -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📋 Учет выполненных работ", callback_data="menu|works-reports"))
    if admin:
        keyboard.row(InlineKeyboardButton(text=f"🛠 Администрирование", callback_data="menu|admin"))
    keyboard.row(InlineKeyboardButton(text=f"⚙️ Настройки", callback_data="menu|settings"))

    return keyboard


def pick_language() -> InlineKeyboardBuilder:
    """Клавиатура для выбора языка"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
    )

    return keyboard