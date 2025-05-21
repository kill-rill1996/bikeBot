from aiogram import Router, F, types
from cache import r
from utils.translator import translator as t

from routers.keyboards import works as kb

router = Router()


@router.callback_query(F.data.split("|")[1] == "works-records")
async def works_reports_menu(callback: types.CallbackQuery) -> None:
    """Меню учета выполненных работ"""
    tg_id = str(callback.from_user.id)
    lang = r.get(f"lang:{tg_id}").decode()

    text = "📋 " + await t.t("work_records", lang)

    keyboard = await kb.works_menu_keyboard(lang)
    await callback.message.edit_text(text=text, reply_markup=keyboard.as_markup())
