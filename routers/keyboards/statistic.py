from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from settings import settings
from utils.translator import translator as t
from utils.date_time_service import convert_date_time, get_days_in_month
from schemas.operations import OperationJobs


async def statistic_period_menu(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода для вывода статистики"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data="works-statistic|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data="works-statistic|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data="works-statistic|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data="works-statistic|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data="works-statistic|custom-period")
    )

    back_button: tuple = await btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def statistic_view_keyboard(lang) -> InlineKeyboardBuilder:
    """Клавиатура для просмотра меню"""
    keyboard = InlineKeyboardBuilder()

    back_button: tuple = await btn.get_back_button("works|works-statistic", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('main_menu', lang)}", callback_data="main-menu"),
    )
    return keyboard


async def select_custom_date(year: int, month: int, lang: str,
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
            callback = f"st_clndr|custom|{d.day}.{d.month}.{d.year}"

        # если выбор первой даты
        else:
            callback = f"statistic_end_date|{d.day}.{d.month}.{d.year}"

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
                             callback_data=f"st_action|{dates_data['prev_month']}|{dates_data['prev_year']}"),
        InlineKeyboardButton(text=f"{next_month_name} {dates_data['next_year']} >>",
                             callback_data=f"st_action|{dates_data['next_month']}|{dates_data['next_year']}")
    )

    # назад
    back_button: tuple = await btn.get_back_button("works|works-statistic", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard
