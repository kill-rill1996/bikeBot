from typing import Any

from aiogram import Router, types
from aiogram.filters import Command

from database.orm import AsyncOrm

from routers.keyboards import menu as kb

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, session: Any, admin: bool) -> None:
    """Обработка команды старт"""
    tg_id = str(message.from_user.id)

    # проверяем существует ли пользователь в БД
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    # если нет, регистрируем его (Имя, язык)
    if not user_exists:
        await AsyncOrm.create_user(session, tg_id, "admin", "ru")
        # TODO исправить потом
        await message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(admin).as_markup())

    # если существует, переводим в главное меню
    else:
        await message.answer("Стартовое сообщение от бота")


@router.message(Command("all"))
async def all_users_count(message: types.Message, session: Any) -> None:
    count = await AsyncOrm.get_users_count(session)
    await message.answer(f"Всего пользователей: {count}")







