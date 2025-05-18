from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn


def works_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"➕ Добавить работу", callback_data="works|add-works"))
    keyboard.row(InlineKeyboardButton(text=f"🗂 Мои работы", callback_data="works|my-works"))
    keyboard.row(InlineKeyboardButton(text=f"📊 Статистика", callback_data="works|works-statistic"))
    keyboard.row(InlineKeyboardButton(text=f"🔍 Поиск транспорта", callback_data="works|search-works"))
    keyboard.row(InlineKeyboardButton(text=f"⚙️ Настройки", callback_data="works|settings"))

    back_button: tuple = btn.get_back_button("main-menu")
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard