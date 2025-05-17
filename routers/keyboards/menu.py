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

