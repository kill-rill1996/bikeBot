from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from schemas.categories_and_jobs import Category
from utils.translator import translator as t

from routers.buttons import buttons as btn


async def jobs_management_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Меню раздела управление операциями"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("add_jobtype", lang), callback_data="jobs-management|add_jobtype")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit_jobtype", lang), callback_data="jobs-management|edit_jobtype")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("add_job", lang), callback_data="jobs-management|add_job")
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit_job", lang), callback_data="jobs-management|edit_job")
    )

    # назад
    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def back_keyboard(lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура назад"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def categories_keyboard(categories: [Category], selected_categories: list[int], lang) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for category in categories:
        text = f"{category.emoji + ' ' if category.emoji else ''}{await t.t(category.title, lang)}"

        # отмечаем выбранные категории
        if category.id in selected_categories:
            text = "✓ " + text

        keyboard.row(
            InlineKeyboardButton(text=text, callback_data=f"add-jobtype-select|{category.id}")
        )

    # готово если есть хоть одна работа
    if len(selected_categories) != 0:
        keyboard.row(InlineKeyboardButton(text=f"✅ {await t.t('done', lang)}", callback_data="select_categories_done"))

    # назад
    back_button: tuple = await btn.get_back_button("jobs-management|add_jobtype", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard



