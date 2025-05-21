from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.translator import translator as t


async def main_menu_keyboard(admin: bool, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📋 {await t.t('work_records', lang)}", callback_data="menu|works-records"))
    if admin:
        keyboard.row(InlineKeyboardButton(text=f"🛠 {await t.t('administration', lang)}", callback_data="menu|admin"))
    keyboard.row(InlineKeyboardButton(text=f"⚙️ {await t.t('settings', lang)}", callback_data="menu|settings"))

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


async def cancel_registration(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для отмены регистрации"""
    keyboard = InlineKeyboardBuilder()
    text = await t.t("cancel", lang)

    keyboard.row(
        InlineKeyboardButton(text=f"❌ {text}", callback_data="cancel_registration")
    )

    return keyboard
