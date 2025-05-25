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


# @router.callback_query(F.data.split("|")[1] == "my-works")
# async def my_works(callback: types.CallbackQuery, tg_id: str, dialog_manager: DialogManager) -> None:
#     """Мои работы"""
#     lang = r.get(f"lang:{tg_id}").decode()
#
#     await dialog_manager.start(MyWorks.select_period, mode=StartMode.RESET_STACK)