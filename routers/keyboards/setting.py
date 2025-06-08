from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.translator import translator as t
from routers.buttons import buttons as btn


async def settings_menu(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню настроек пользователя"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{await t.t('change_lang', lang)}", callback_data="settings|change_language"))

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"main-menu", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def choose_lang_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора языка в настройках"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="change_lang|ru"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="change_lang|en"),
        InlineKeyboardButton(text="🇪🇸 Español", callback_data="change_lang|es"),
    )

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"menu|settings", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard