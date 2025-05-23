from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Job
from schemas.location import Location
from utils.translator import translator as t
from schemas.categories_and_jobs import Category, Subcategory, Jobtype


async def add_works_menu_keyboard(categories: List[Category], lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню добавить работу с выбором категории"""
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        # учитываем возможность отсутствия эмоджи
        text = f"{c.emoji + ' ' if c.emoji else ''}" + await t.t(c.title, lang)
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"vehicle_category|{c.id}"))

    # keyboard.row(InlineKeyboardButton(text=f"{t.t('bicycles', lang)}", callback_data="vehicle_category|bicycles"))
    # keyboard.row(InlineKeyboardButton(text=f"{t.t('ebicycles', lang)}", callback_data="vehicle_category|ebicycles"))
    # keyboard.row(InlineKeyboardButton(text=f"{t.t('segways', lang)}", callback_data="vehicle_category|segways"))
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('recent_works', lang)}", callback_data="recent_works"))

    back_button: tuple = await btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def select_subcategory_keyboard(subcategories: List[Subcategory], lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора подкатегории (только для категории велосипеды)"""
    keyboard = InlineKeyboardBuilder()

    # подкатегории
    # title для использования в тексте хендлера
    for sc in subcategories:
        keyboard.row().add(InlineKeyboardButton(text=f"{sc.title}", callback_data=f"vehicle_subcategory|{sc.id}|{sc.title}"))

    # подкатегории
    # keyboard.row(
    #     InlineKeyboardButton(text=f"U", callback_data="vehicle_subcategory|U"),
    #     InlineKeyboardButton(text=f"H", callback_data="vehicle_subcategory|H"),
    #     InlineKeyboardButton(text=f"C", callback_data="vehicle_subcategory|C")
    # )

    # назад
    back_button: tuple = await btn.get_back_button("works|add-works", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_bicycle_number(category_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для ввода номера велосипеда после выбора подкатегории"""
    keyboard = InlineKeyboardBuilder()

    # последние обслуженные
    # TODO доделать
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('recently_serviced', lang)}", callback_data="recently_serviced"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_choose_subcategory|{category_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_work_category(jobtypes: List[Jobtype], category_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора категории работы"""
    keyboard = InlineKeyboardBuilder()

    for jobtype in jobtypes:
        # учитываем возможность отсутствия эмоджи
        text = f"{jobtype.emoji + ' ' if jobtype.emoji else ''}" + await t.t(jobtype.title, lang)
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"work_jobtype|{jobtype.id}"))

    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('brake_system', lang)}", callback_data="work_category|brake_system"))
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('transmission_and_chain', lang)}", callback_data="work_category|transmission_and_chain"))
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('wheels_and_tires', lang)}", callback_data="work_category|wheels_and_tires"))
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('steering', lang)}", callback_data="work_category|steering"))
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('frame_and_suspension', lang)}", callback_data="work_category|frame_and_suspension"))
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('electrical_and_lighting', lang)}", callback_data="work_category|electrical_and_lighting"))

    # прочие
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('other', lang)}", callback_data="other"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_choose_subcategory|{category_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_jobs_keyboard(jobs: List[Job], category_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для выбора jobs после выбора группы узлов"""
    keyboard = InlineKeyboardBuilder()

    for job in jobs:
        text = await t.t(job.title, lang)
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"work_job|{job.id}"))

    # готово
    # todo доделать
    keyboard.row(InlineKeyboardButton(text=f"✅ {await t.t('done', lang)}", callback_data="done"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_jobtype|{category_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def back_from_duration(jobtype_id: int, lang: str) -> InlineKeyboardBuilder:
    """При вводе времени работы"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_work_jobtype|{jobtype_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_location(locations: List[Location], job_id: int, lang: str) -> InlineKeyboardBuilder:
    """Для выбора локации"""
    keyboard = InlineKeyboardBuilder()

    for location in locations:
        text = await t.t(location.name, lang)
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"work_location|{location.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_work_job|{job_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard
