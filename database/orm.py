import datetime
from typing import Any

from logger import logger


class AsyncOrm:

    @staticmethod
    async def check_user_already_exists(tg_id: str, session: Any) -> bool:
        """Проверяет создан ли профиль пользователя в БД"""
        try:
            exists = await session.fetchval(
                """
                SELECT EXISTS(SELECT 1 FROM users WHERE tg_id = $1)
                """,
                tg_id
            )
            return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке регистрации пользователя {tg_id}: {e}")


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
    async def create_user(session: Any, tg_id: str, role: str, lang: str):
        """Создает пользователя"""
        created_at = datetime.datetime.now()
        try:
            await session.execute(
                """
                INSERT INTO users(tg_id, created_at, role, lang)
                VALUES ($1, $2, $3, $4)
                """,
                tg_id, created_at, role, lang
            )
            logger.info(f"Зарегистрировался пользователь tg_id: {tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя tg_id {tg_id}: {e}")
