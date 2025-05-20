import datetime
from typing import Any, List

from logger import logger

from schemas.users import User


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
    async def create_user(session: Any, tg_id: str, tg_username: str, username: str, role: str, lang: str):
        """Создает пользователя"""
        created_at = datetime.datetime.now()
        try:
            await session.execute(
                """
                INSERT INTO users(tg_id, tg_username, username, created_at, role, lang)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                tg_id, tg_username, username, created_at, role, lang
            )
            logger.info(f"Успешно создан пользователь tg_id: {tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя tg_id {tg_id}: {e}")

    @staticmethod
    async def get_user_by_tg_id(session: Any, tg_id: str) -> User:
        """Получает пользователя"""
        try:
            row = await session.fetch(
                """
                SELECT * FROM users
                WHERE tg_id=$1
                """,
                tg_id
            )
            user = User.model_validate(row)
            return user

        except Exception as e:
            logger.error(f"Ошибка при получении пользователя {tg_id}: {e}")

    @staticmethod
    async def get_user_language(session: Any, tg_id: str) -> str:
        """Получение языка пользователя"""
        try:
            lang = await session.fetchval(
                """
                SELECT lang FROM users
                WHERE tg_id=$1
                """,
                tg_id
            )
            return lang

        except Exception as e:
            logger.error(f"Ошибка при получении языка пользователя {tg_id}: {e}")

    @staticmethod
    async def get_allow_users(session: Any) -> List[str]:
        """Получение id всех пользователей из allowed_users"""
        try:
            query = await session.fetch(
                """
                SELECT tg_id
                FROM allowed_users
                """,
            )

            ids = [row["tg_id"] for row in query]
            return ids

        except Exception as e:
            logger.error(f"Ошибка получения всех id из allowed_users: {e}")

    @staticmethod
    async def change_user_language(tg_id: str, lang: str, session: Any) -> None:
        """Смена языка пользователя"""
        try:
            await session.execute(
                """
                UPDATE users 
                SET lang = $1
                WHERE tg_id = $2 
                """,
                lang, tg_id
            )
            logger.info(f"Пользователь {tg_id} сменил язык на {lang.upper()}")
        except Exception as e:
            logger.error(f"Ошибка при смене языка пользователя {tg_id} на {lang.upper()}: {e}")