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

    # # последние обслуженные
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('recent_works', lang)}", callback_data="recent_works"))

    back_button: tuple = await btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def select_subcategory_keyboard(subcategories: List[Subcategory], lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора подкатегории (только для категории велосипеды)"""
    keyboard = InlineKeyboardBuilder()

    # подкатегории
    for sc in subcategories:
        keyboard.row().add(InlineKeyboardButton(text=f"{sc.title}", callback_data=f"vehicle_subcategory|{sc.id}|{sc.title}"))

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
    # keyboard.row(InlineKeyboardButton(text=f"{await t.t('recently_serviced', lang)}", callback_data="recently_serviced"))

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

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_choose_subcategory|{category_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_jobs_keyboard(jobs: List[Job], page: int, category_id: int, lang: str, selected_jobs: list[int]) -> InlineKeyboardBuilder:
    """Клавиатура для выбора jobs после выбора группы узлов с пагинацией"""
    keyboard = InlineKeyboardBuilder()

    # pagination
    nums_on_page = 4
    pages = get_page_nums(len(jobs), nums_on_page)

    # при переходе с первой на последнюю
    if page == 0:
        page = pages

    # при переходе с последней на первую
    if page > pages:
        page = 1

    start = (page - 1) * nums_on_page
    end = page * nums_on_page

    jobs_sorted = []
    for job in jobs:
        translated_title = await t.t(job.title, lang)
        job.title = translated_title
        jobs_sorted.append(job)

    jobs_sorted = sorted(jobs_sorted, key=lambda j: j.title)

    page_jobs = jobs_sorted[start:end]

    for job in page_jobs:
        text = await t.t(job.title, lang)

        # помечаем выбранные
        if job.id in selected_jobs:
            text = "✓ " + text

        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"work_job_select|{job.id}|{page}"))

    # готово если есть хоть одна работа
    if len(selected_jobs) != 0:
        keyboard.row(InlineKeyboardButton(text=f"✅ {await t.t('done', lang)}", callback_data="work_job_done"))

    # pages
    if len(jobs) > nums_on_page:
        keyboard.row(
            InlineKeyboardButton(text=f"<", callback_data=f"prev|{page}"),
            InlineKeyboardButton(text=f"{page}/{pages}", callback_data="pages"),
            InlineKeyboardButton(text=f">", callback_data=f"next|{page}")
        )

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


async def select_location(locations: List[Location], lang: str) -> InlineKeyboardBuilder:
    """Для выбора локации"""
    keyboard = InlineKeyboardBuilder()

    for location in locations:
        text = await t.t(location.name, lang)
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"work_location|{location.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_work_job", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def back_from_comment_keyboard(duration: int, lang: str) -> InlineKeyboardBuilder:
    """"Клавиатура для возврата назад из комментария"""
    keyboard = InlineKeyboardBuilder()

    # продолжить
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('continue', lang)}", callback_data="continue"))

    # назад
    back_button: tuple = await btn.get_back_button(f"back_to_work_location|{duration}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def preview_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для предпросмотра"""
    keyboard = InlineKeyboardBuilder()

    # подтвердить
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('confirm', lang)}", callback_data="confirm"))

    # отменить
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('cancel', lang)}", callback_data="cancel"))

    return keyboard


async def work_saved_keyboard(category_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура после сохранения работы"""
    keyboard = InlineKeyboardBuilder()

    # Записать еще работу
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('another_work', lang)}", callback_data=f"another_work|{category_id}"))

    # Главное меню
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('main_menu', lang)}", callback_data="main-menu"))

    return keyboard


async def second_confirmation_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура повторного подтверджения работы"""
    keyboard = InlineKeyboardBuilder()

    # да
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('yes', lang)}", callback_data="yes"))

    # нет
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('no', lang)}", callback_data="no"))

    return keyboard


def get_page_nums(items: int, nums_on_page: int) -> int:
    """Получение количества страниц"""
    pages = items // nums_on_page

    if items - pages * nums_on_page != 0:
        pages += 1

    return pages