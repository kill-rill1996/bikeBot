import datetime
from typing import Any

from logger import logger


class AsyncOrm:

    @staticmethod
    async def get_users_count(session: Any):
        """Вывод числа всех пользователей"""
        try:
            exists = await session.fetchval(
                """
                SELECT COUNT(*) 
                FROM users
                """
            )
            return exists
        except Exception as e:
            logger.error(f"Ошибка при выводе кол-ва пользователей: {e}")

    @staticmethod
    async def create_user(session: Any, tg_id: str):
        """Создает пользователя"""
        created_at = datetime.datetime.now()
        try:
            await session.execute(
                """
                INSERT INTO users(tg_id, created_at)
                VALUES ($1, $2)
                """,
                tg_id, created_at
            )
            logger.info(f"Зарегистрировался пользователь tg_id: {tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя tg_id {tg_id}: {e}")
