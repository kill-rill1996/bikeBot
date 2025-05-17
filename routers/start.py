from typing import Any

from aiogram import Router, types
from aiogram.filters import Command

from database.orm import AsyncOrm

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, session: Any) -> None:
    """Обработка команды старт"""
    tg_id = str(message.from_user.id)
    await AsyncOrm.create_user(session, tg_id)

    await message.answer("Стартовое сообщение от бота")


@router.message(Command("all"))
async def all_users_count(message: types.Message, session: Any) -> None:
    count = await AsyncOrm.get_users_count(session)
    await message.answer(f"Всего пользователей: {count}")







