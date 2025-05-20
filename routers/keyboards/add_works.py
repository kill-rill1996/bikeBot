from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from utils.translator import translator as t


def add_works_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню добавить работу с выбором категории"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{t.t('bicycles', lang)}", callback_data="vehicle_category|bicycles"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('ebicycles', lang)}", callback_data="vehicle_category|ebicycles"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('segways', lang)}", callback_data="vehicle_category|segways"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('recent_works', lang)}", callback_data="vehicle_category|recent_works"))

    back_button: tuple = btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


def select_subcategory_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора подкатегории (только для категории велосипеды)"""
    keyboard = InlineKeyboardBuilder()

    # подкатегории
    keyboard.row(
        InlineKeyboardButton(text=f"U", callback_data="vehicle_subcategory|U"),
        InlineKeyboardButton(text=f"H", callback_data="vehicle_subcategory|H"),
        InlineKeyboardButton(text=f"C", callback_data="vehicle_subcategory|C")
    )

    # назад
    back_button: tuple = btn.get_back_button("works|add-works", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


def select_bicycle_number(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для ввода номера велосипеда после выбора подкатегории"""
    keyboard = InlineKeyboardBuilder()

    # последние обслуженные
    # TODO доделать
    keyboard.row(InlineKeyboardButton(text=f"{t.t('recently_serviced', lang)}", callback_data="recently_serviced"))

    # назад
    back_button: tuple = btn.get_back_button("back_to_choose_subcategory|bicycles", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


def select_work_category(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора категории работы"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{t.t('brake_system', lang)}", callback_data="work_category|brake_system"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('transmission_and_chain', lang)}", callback_data="work_category|transmission_and_chain"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('wheels_and_tires', lang)}", callback_data="work_category|wheels_and_tires"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('steering', lang)}", callback_data="work_category|steering"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('frame_and_suspension', lang)}", callback_data="work_category|frame_and_suspension"))
    keyboard.row(InlineKeyboardButton(text=f"{t.t('electrical_and_lighting', lang)}", callback_data="work_category|electrical_and_lighting"))

    # прочие
    keyboard.row(InlineKeyboardButton(text=f"{t.t('other', lang)}", callback_data="work_category|other"))

    # назад
    back_button: tuple = btn.get_back_button("works|add-works", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))


    return keyboard
