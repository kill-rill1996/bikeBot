from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from settings import settings
from utils.translator import translator as t
from utils.date_time_service import convert_date_time, get_days_in_month
from schemas.operations import OperationJobs


async def works_period_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора периода для вывода моих работ"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('today', lang)}", callback_data="my-works|today"),
        InlineKeyboardButton(text=f"{await t.t('yesterday', lang)}", callback_data="my-works|yesterday"),
        InlineKeyboardButton(text=f"{await t.t('week', lang)}", callback_data="my-works|week"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{await t.t('month', lang)}", callback_data="my-works|month"),
        InlineKeyboardButton(text=f"{await t.t('custom_period', lang)}", callback_data="my-works|custom-period")
    )

    back_button: tuple = await btn.get_back_button("menu|works-records", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
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
            callback = f"w_clndr|custom|{d.day}.{d.month}.{d.year}"

        # если выбор первой даты
        else:
            callback = f"works_end_date|{d.day}.{d.month}.{d.year}"

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
                             callback_data=f"w_action|{dates_data['prev_month']}|{dates_data['prev_year']}"),
        InlineKeyboardButton(text=f"{next_month_name} {dates_data['next_year']} >>",
                             callback_data=f"w_action|{dates_data['next_month']}|{dates_data['next_year']}")
    )

    # назад
    back_button: tuple = await btn.get_back_button("works|my-works", lang)
    keyboard.row(InlineKeyboardButton(text=back_button[0], callback_data=back_button[1]))

    return keyboard


async def works_my_works_list(lang: str, works: list[OperationJobs], period: str) -> InlineKeyboardBuilder:
    """Вывод списка работ в кнопках"""
    keyboard = InlineKeyboardBuilder()

    for w in works:
        # формируем данные с переводом
        date, time = convert_date_time(w.created_at, True)
        transport_category = await t.t(w.transport_category, lang)
        jobtype_title = await t.t(w.jobtype_title, lang)

        # в callback добавляем период, чтобы в след. хэндлере можно было его использовать в кнопке назад
        keyboard.row(
            InlineKeyboardButton(
                text=f"{date} {time} | ID {w.id} | {transport_category} | {w.transport_subcategory}-{w.serial_number} | {jobtype_title}",
                callback_data=f"my-works-list|{w.id}|{period}"
            )
        )

    # назад
    back_button: tuple = await btn.get_back_button("works|my-works", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def work_details(lang: str, operation_id: int, period: str) -> InlineKeyboardBuilder:
    """Клавиатура вывода деталей про работу"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit", lang), callback_data=f"edit-work|{operation_id}|{period}"),
    )
    keyboard.row(
        InlineKeyboardButton(text=await t.t("delete", lang), callback_data=f"delete-work|{operation_id}|{period}")
    )

    # кнопка назад
    # back_button: tuple = await btn.get_back_button(f"back-from-works-list-custom|{period}", lang)
    # keyboard.row(
    #     InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    # )
    # кнопка главное меню
    keyboard.row(
        InlineKeyboardButton(text=await t.t("main_menu", lang), callback_data="menu|works-records")
    )

    return keyboard


async def back_keyboard(lang: str, period: str, operation_id: int) -> InlineKeyboardBuilder:
    """Клавиатура назад когда уже нельзя менять работу"""
    keyboard = InlineKeyboardBuilder()

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"my-works-list|{operation_id}|{period}", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def confirm_edit_comment_keyboard(lang: str, operation_id: int, period: str) -> InlineKeyboardBuilder:
    """Клавиатура назад когда уже нельзя менять работу"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("save_changes", lang), callback_data="save-changes-comment")
    )

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"my-works-list|{operation_id}|{period}", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )

    return keyboard


async def after_comment_updated_keyboard(lang: str) -> InlineKeyboardBuilder:
    """Клавиатура после успешного изменения комментария"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"🗂 {await t.t('my_works', lang)}", callback_data="works|my-works"))
    keyboard.row(InlineKeyboardButton(text=await t.t("main_menu", lang), callback_data="main-menu"))

    return keyboard


async def delete_work(lang: str, operation_id: int, period: str) -> InlineKeyboardBuilder:
    """Предложение удалить работу"""
    keyboard = InlineKeyboardBuilder()

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"my-works-list|{operation_id}|{period}", lang)

    keyboard.row(
        InlineKeyboardButton(text=await t.t("yes", lang), callback_data=f"delete-work-confirm|{operation_id}"),
        InlineKeyboardButton(text=await t.t("no", lang), callback_data=back_button[1]),
    )

    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard
