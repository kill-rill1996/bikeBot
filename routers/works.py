from aiogram import Router, F, types

from routers.keyboards import works as kb

router = Router()


@router.callback_query(F.data.split("|")[1] == "works-reports")
async def works_reports_menu(callback: types.CallbackQuery) -> None:
    """Меню учета выполненных работ"""
    await callback.message.edit_text(text="Учет выполненных работ", reply_markup=kb.works_menu_keyboard().as_markup())
