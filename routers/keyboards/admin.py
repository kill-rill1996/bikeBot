import calendar
from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.categories_and_jobs import Subcategory, Jobtype, Category
from schemas.location import Location
from schemas.transport import TransportSubcategory
from schemas.users import User
from settings import settings
from utils.date_time_service import get_days_in_month
from utils.translator import translator as t


async def admin_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📑 {await t.t('reports', lang)}", callback_data="admin|reports"))
    keyboard.row(InlineKeyboardButton(text=f"🚗 {await t.t('vehicle_management', lang)}", callback_data="admin|vehicle_management"))
    keyboard.row(InlineKeyboardButton(text=f"🌎 {await t.t('location_management', lang)}", callback_data="admin|location_management"))
    keyboard.row(InlineKeyboardButton(text=f"🛠 {await t.t('operation_management', lang)}", callback_data="admin|operation_management"))
    keyboard.row(InlineKeyboardButton(text=f"👤 {await t.t('user_management', lang)}", callback_data="admin|user_management"))
    keyboard.row(InlineKeyboardButton(text=f"🗑️ {await t.t('delete_work', lang)}", callback_data="admin|delete_work"))

    back_button: tuple = await btn.get_back_button("main-menu", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def reports_menu_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура меню отчетов администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('individual_mechanic_report', lang)}", callback_data="admin-reports|individual_mechanic_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('summary_report_by_mechanics', lang)}", callback_data="admin-reports|summary_report_by_mechanics"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('vehicle_report', lang)}", callback_data="admin-reports|vehicle_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('work_categories_report', lang)}", callback_data="admin-reports|work_categories_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('inefficiency_report', lang)}", callback_data="admin-reports|inefficiency_report"))
    keyboard.row(InlineKeyboardButton(text=f"📆 {await t.t('location_report', lang)}", callback_data="admin-reports|location_report"))

    back_button: tuple = await btn.get_back_button("menu|admin", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_period_keyboard(report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода отчета"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data=f"reports-period|{report_type}|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data=f"reports-period|{report_type}|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data=f"reports-period|{report_type}|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data=f"reports-period|{report_type}|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data=f"reports-period|{report_type}|custom")
    )

    # назад
    back_button: tuple = await btn.get_back_button("admin|reports", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))
    return keyboard


async def select_custom_date(report_type: str, year: int, month: int, lang: str,
                             dates_data: dict, end_date: bool = None) -> InlineKeyboardBuilder:
    """Клавиатура выбора кастомного периода"""
    keyboard = InlineKeyboardBuilder()

    # получаем дни в месяце датами
    month_days = get_days_in_month(year, month)

    # заголовок клавиатуры
    header = f"🗓️ {settings.calendar_months[lang][month]} {year}"
    keyboard.add(InlineKeyboardButton(text=header, callback_data="ignore"))

    # дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.row(*[InlineKeyboardButton(text=day, callback_data='ignore') for day in week_days])

    buttons = []

    # отступ для первого дня в месяце
    buttons += [InlineKeyboardButton(text=" ", callback_data="ignore")] * (month_days[0].weekday())

    # кнопки по дням месяца
    for d in month_days:
        # если выбор второй даты
        if end_date:
            callback = f"clndr|{report_type}|custom|{d.day}.{d.month}.{d.year}"

        # если выбор первой даты
        else:
            callback = f"select_end_date|{report_type}|{d.day}.{d.month}.{d.year}"

        buttons.append(InlineKeyboardButton(text=str(d.day), callback_data=f'{callback}'))

    # отступ после последнего дня
    buttons += [InlineKeyboardButton(text=" ", callback_data="ignore")] * (6 - month_days[-1].weekday())

    # разбиваем по 7 штук в строке
    for i in range(0, len(buttons), 7):
        keyboard.row(*buttons[i:i + 7])

    # кнопки следующего месяца и предыдущего
    prev_month_name = settings.calendar_months[lang][dates_data["prev_month"]]
    next_month_name = settings.calendar_months[lang][dates_data["next_month"]]
    keyboard.row(
        InlineKeyboardButton(text=f"<< {prev_month_name} {dates_data['prev_year']}",
                             callback_data=f"action|{report_type}|{dates_data['prev_month']}|{dates_data['prev_year']}"),
        InlineKeyboardButton(text=f"{next_month_name} {dates_data['next_year']} >>",
                             callback_data=f"action|{report_type}|{dates_data['next_month']}|{dates_data['next_year']}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def choose_mechanic(mechanics: List[User], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора механика"""
    keyboard = InlineKeyboardBuilder()

    for mechanic in mechanics:
        keyboard.row(InlineKeyboardButton(text=mechanic.username, callback_data=f"mechanic|{period}|{mechanic.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def back_to_mechanic(period: str, report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору механика"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def back_to_location(period: str, report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору местоположения"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def select_vehicle_report_type(report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор отчет по подкатегории или по конкретному транспорту"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('by_category', lang)}", callback_data=f"vehicle_report_type|by_category|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('by_subcategory', lang)}", callback_data=f"vehicle_report_type|by_subcategory|{report_type}|{period}")
    )
    keyboard.row(InlineKeyboardButton(text=f"{await t.t('by_transport', lang)}", callback_data=f"vehicle_report_type|by_transport|{report_type}|{period}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_vehicle_subcategory(subcategories: List[Subcategory], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор подкатегории для отчета по транспорту"""
    keyboard = InlineKeyboardBuilder()

    for sc in subcategories:
        keyboard.row(InlineKeyboardButton(text=sc.title, callback_data=f"vehicle_report_by_sc|{report_type}|{period}|{sc.id}"))

    keyboard.adjust(3)

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_vehicle_category(categories: List[Category], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор категории для отчета по транспорту"""
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        emoji = c.emoji + " " if c.emoji else ""
        keyboard.row(InlineKeyboardButton(text=emoji + await t.t(c.title, lang), callback_data=f"vehicle_report_by_c|{report_type}|{period}|{c.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_category_for_jobtypes_report(categories: List[Category], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор категории для отчета по jobtypes"""
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        emoji = c.emoji + " " if c.emoji else ""
        keyboard.row(InlineKeyboardButton(text=emoji + await t.t(c.title, lang), callback_data=f"jobtypes_report_category|{report_type}|{period}|{c.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_category_for_transport_report(categories: List[Category], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор категории для отчета по серийному номеру транспорта"""
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        emoji = c.emoji + " " if c.emoji else ""
        keyboard.row(InlineKeyboardButton(text=emoji + await t.t(c.title, lang), callback_data=f"transport_report_category|{report_type}|{period}|{c.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_subcategory_for_transport_report(subcategories: List[Subcategory], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Выбор подкатегории для отчета по серийному номеру транспорта"""
    keyboard = InlineKeyboardBuilder()

    for sc in subcategories:
        keyboard.row(InlineKeyboardButton(text=sc.title, callback_data=f"transport_report_subcategory|{report_type}|{period}|{sc.id}"))

    keyboard.adjust(3)

    # назад
    back_button: tuple = await btn.get_back_button(f"vehicle_report_type|by_transport|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def back_to(report_sub_type: str, period: str, report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"vehicle_report_type|{report_sub_type}|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def transport_pagination_keyboard(transports: List[TransportSubcategory], page: int, report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура пагинации для выбора транспорта"""
    keyboard = InlineKeyboardBuilder()

    # pagination
    nums_on_page = 24
    pages = get_page_nums(len(transports), nums_on_page)

    # при переходе с первой на последнюю
    if page == 0:
        page = pages

    # при переходе с последней на первую
    if page > pages:
        page = 1

    start = (page - 1) * nums_on_page
    end = page * nums_on_page
    page_transports = transports[start:end]

    for transport in page_transports:
        text = f"{transport.subcategory_title}-{transport.serial_number}"

        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"vehicle_report_by_t|{report_type}|{period}|{transport.id}"))

    keyboard.adjust(4)

    # pages
    if len(transports) > nums_on_page:
        keyboard.row(
            InlineKeyboardButton(text=f"<", callback_data=f"prev|{page}|{report_type}|{period}"),
            InlineKeyboardButton(text=f"{page}/{pages}", callback_data="pages"),
            InlineKeyboardButton(text=f">", callback_data=f"next|{page}|{report_type}|{period}")
        )

    # назад
    category_id = transports[0].category_id
    back_button: tuple = await btn.get_back_button(f"transport_report_category|{report_type}|{period}|{category_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_jobtypes(jobtypes: List[Jobtype], selected: List[int], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура мультивыбора jobtypes"""
    keyboard = InlineKeyboardBuilder()

    for jt in jobtypes:
        emoji = jt.emoji + " " if jt.emoji else ""
        text = emoji + await t.t(jt.title, lang)

        # помечаем выбранные
        if jt.id in selected:
            text = "✓ " + text

        keyboard.row(InlineKeyboardButton(text=text, callback_data=f"jobtypes_select|{jt.id}|{report_type}|{period}"))

    if len(selected) != 0:
        keyboard.row(InlineKeyboardButton(text=f"✅ {await t.t('done', lang)}", callback_data=f"jobtype_select_done|{report_type}|{period}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def select_location(locations: List[Location], report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора локации"""
    keyboard = InlineKeyboardBuilder()

    for location in locations:
        keyboard.row(InlineKeyboardButton(text=await t.t(location.name, lang), callback_data=f"select_location|{report_type}|{period}|{location.id}"))

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def back_to_choose_period(report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору периода для отчета по неэффективности"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def mechanic_report_details_keyboard(period: str, report_type: str, user_id: int, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору механика"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}|{user_id}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic-mechanic|{period}|{user_id}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"reports-period|{report_type}|{period}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def summary_report_details_keyboard(report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору периода"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic-mechanics|{period}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def vehicle_report_details_keyboard(back_to: str, period: str, report_type: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору периода"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic-transport|{period}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(back_to, lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def jobtypes_report_details_keyboard(report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура возврата к выбору jobtypes"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic-jobtypes|{period}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def efficient_report_details_keyboard(report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура отчета по неэффективности"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        # TODO поправить
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def location_report_details_keyboard(report_type: str, period: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура отчета по местоположению"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('excel_export', lang)}", callback_data=f"excel_export|{report_type}|{period}"),
        InlineKeyboardButton(text=f"{await t.t('graphic', lang)}", callback_data=f"graphic-location|{period}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"admin-reports|{report_type}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


async def excel_ready_keyboard(back_callback: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура отчета по неэффективности"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"{back_callback}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    # главное меню
    main_menu_button: tuple = await btn.get_main_menu_button(lang)
    keyboard.row(InlineKeyboardButton(text=main_menu_button[0], callback_data=main_menu_button[1]))

    return keyboard


def get_page_nums(items: int, nums_on_page: int) -> int:
    """Получение количества страниц"""
    pages = items // nums_on_page

    if items - pages * nums_on_page != 0:
        pages += 1

    return pages


async def back_keyboard(back_callback: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура для возвращения назад"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(f"{back_callback}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard