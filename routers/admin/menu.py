from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from routers.keyboards import admin as kb
from utils.translator import translator as t
from cache import r

router = Router()


@router.callback_query(F.data == "menu|admin")
async def show_main_menu(callback: types.CallbackQuery, tg_id: str, state: FSMContext) -> None:
    """Меню администратора"""
    try:
        await state.clear()
    except Exception:
        pass

    lang = r.get(f"lang:{tg_id}").decode()

    text = await t.t("section_menu", lang)

    keyboard = await kb.admin_menu_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())



