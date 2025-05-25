from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.buttons import buttons as btn
from utils.translator import translator as t
from utils.date_time_service import convert_date_time
from schemas.operations import OperationShow


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


async def works_my_works_list(lang: str, works: list[OperationShow], period: str) -> InlineKeyboardBuilder:
    """Вывод списка работ в кнопках"""
    keyboard = InlineKeyboardBuilder()

    for w in works:
        # формируем данные с переводом
        created_at = convert_date_time(w.created_at, True)[0]
        transport_category = await t.t(w.transport_category, lang)
        job_title = await t.t(w.job_title, lang)

        # в callback добавляем период, чтобы в след. хэндлере можно было его использовать в кнопке назад
        keyboard.row(
            InlineKeyboardButton(
                text=f"{created_at}|{w.id}|{transport_category}|{w.transport_subcategory}-{w.serial_number}|{job_title}",
                callback_data=f"my-works-list|{w.id}|{period}"
            )
        )

    back_button: tuple = await btn.get_back_button("works|my-works", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    return keyboard


async def work_details(lang: str, operation_id: int, period: str) -> InlineKeyboardBuilder:
    """Клавиатура вывода деталей про работу"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=await t.t("edit", lang), callback_data=f"edit-work|{operation_id}"),
        InlineKeyboardButton(text=await t.t("delete", lang), callback_data=f"delete-work|{operation_id}")
    )

    # кнопка назад
    back_button: tuple = await btn.get_back_button(f"my-works|{period}", lang)
    keyboard.row(
        InlineKeyboardButton(text=back_button[0], callback_data=back_button[1])
    )
    # кнопка главное меню
    keyboard.row(
        InlineKeyboardButton(text=await t.t("main_menu", lang), callback_data="main-menu")
    )

    return keyboard
