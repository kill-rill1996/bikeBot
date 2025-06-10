from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from schemas.search import TransportNumber, OperationJobsUserLocation
from utils.translator import translator as t
from utils.date_time_service import convert_date_time, get_days_in_month
from settings import settings


async def back_keyboard(lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура назад"""
    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def transport_jobs_keyboard(lang: str, transports: list[TransportNumber]) -> InlineKeyboardBuilder:
    """Клавиатура вывода найденных транспортов и работ"""
    keyboard = InlineKeyboardBuilder()

    # кнопки с транспортом
    for transport in transports:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{transport.subcategory_title}-{transport.serial_number}",
                callback_data=f"searched_transport|{transport.id}"
            )
        )
    keyboard.adjust(3)

    # назад
    back_button: tuple = await btn.get_back_button("works|search-vehicle", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def transport_period_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода для вывода моих работ"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data="search_period|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data="search_period|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data="search_period|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data="search_period|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data="search_period|custom-period")
    )

    back_button: tuple = await btn.get_back_button("works|search-vehicle", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def found_operations_keyboard(
        operations: [OperationJobsUserLocation], lang: str, callback_data: str) -> InlineKeyboardBuilder:
    """Клавиатура назад"""
    keyboard = InlineKeyboardBuilder()

    # формируем из операций кнопки в формате date: ID|category|subcat-sn
    for operation in operations:
        date = convert_date_time(operation.created_at, True)[0]
        text = f"{date}: {operation.id} | {await t.t(operation.category_title, lang)} | " \
               f"{operation.subcategory_title}-{operation.serial_number}"
        keyboard.row(
            InlineKeyboardButton(text=text, callback_data=f"operation-detail|{operation.id}"),
        )

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def back_and_main_menu_keyboard(callback_data: str, lang: str) -> InlineKeyboardBuilder:
    """Клавиатура в главное меню и назад"""

    keyboard = InlineKeyboardBuilder()

    # назад
    back_button: tuple = await btn.get_back_button(callback_data, lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    # кнопка главное меню
    keyboard.row(
        InlineKeyboardButton(text=await t.t("main_menu", lang), callback_data="main-menu")
    )

    return keyboard


async def select_custom_date(year: int, month: int, lang: str,
                             dates_data: dict, transport_id: int, end_date: bool = None) -> InlineKeyboardBuilder:
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
            callback = f"se_clndr|custom|{d.day}.{d.month}.{d.year}"

        # если выбор первой даты
        else:
            callback = f"search_end_date|{d.day}.{d.month}.{d.year}"

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
                             callback_data=f"se_action|{dates_data['prev_month']}|{dates_data['prev_year']}"),
        InlineKeyboardButton(text=f"{next_month_name} {dates_data['next_year']} >>",
                             callback_data=f"se_action|{dates_data['next_month']}|{dates_data['next_year']}")
    )

    # назад
    back_button: tuple = await btn.get_back_button(f"searched_transport|{transport_id}", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard