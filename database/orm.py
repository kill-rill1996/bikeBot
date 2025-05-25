import datetime
import asyncpg
from collections.abc import Mapping
from typing import Any, List

from logger import logger
from schemas.categories_and_jobs import Category, Subcategory, Jobtype, Job
from schemas.location import Location
from schemas.operations import Operation, OperationAdd

from schemas.users import User


Mapping.register(asyncpg.Record)


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
    async def create_user(session: Any, tg_id: str, tg_username: str, username: str,
                          role: str, lang: str, is_active: bool = True):
        """Создает пользователя"""
        created_at = datetime.datetime.now()
        try:
            await session.execute(
                """
                INSERT INTO users(tg_id, tg_username, username, created_at, role, lang, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                tg_id, tg_username, username, created_at, role, lang, is_active
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

    @staticmethod
    async def get_all_categories(session: Any) -> List[Category]:
        """Получение всех категорий транспорта"""
        try:
            rows = await session.fetch(
                """
                SELECT id, title, emoji 
                FROM categories;
                """
            )

            categories = [Category.model_validate(row) for row in rows]
            return categories

        except Exception as e:
            logger.error(f"Ошибка при получение всех категорий транспорта: {e}")

    @staticmethod
    async def get_category_by_id(category_id: int, session: Any) -> Category:
        """Получение категории по id"""
        try:
            row = await session.fetchrow(
                """
                SELECT *
                FROM categories
                WHERE id = $1
                """,
                category_id
            )

            return Category.model_validate(row)
        except Exception as e:
            logger.error(f"Ошибка при получении категории с id {category_id}: {e}")

    @staticmethod
    async def get_subcategories_by_category(category_id: int, session: Any) -> List[Subcategory]:
        """Получение подкатегорий для категории"""
        try:
            rows = await session.fetch(
                """
                SELECT * 
                FROM subcategories
                WHERE category_id = $1;
                """,
                category_id
            )

            subcategories = [Subcategory.model_validate(row) for row in rows]
            return subcategories

        except Exception as e:
            logger.error(f"Ошибка при получение всех подкатегорий для категории транспорта с id {category_id}: {e}")

    @staticmethod
    async def get_subcategory_by_id(subcategory_id: int, session: Any) -> Subcategory:
        """Получение подкатегории по id"""
        try:
            row = await session.fetchrow("""
                SELECT *
                FROM subcategories
                WHERE id = $1
                """, subcategory_id)

            return Subcategory.model_validate(row)
        except Exception as e:
            logger.error(f"Ошибка при получении подкатегории с id {subcategory_id}: {e}")

    @staticmethod
    async def get_sn_by_category_and_subcategory(category_id: int, subcategory_id: int, session: Any) -> List[int]:
        """Получение серийных номеров транспорта по категории и подкатегории"""
        try:
            rows = await session.fetch(
                """
                SELECT serial_number
                FROM transports
                WHERE category_id = $1 AND subcategory_id = $2;
                """,
                category_id, subcategory_id
            )

            serial_numbers = [row['serial_number'] for row in rows]
            return serial_numbers
        except Exception as e:
            logger.error(f"Ошибка при получение серийных номеров транспорта для "
                         f"категории {category_id} и подкатегории {subcategory_id}: {e}")

    @staticmethod
    async def get_transport_id(category_id: int, subcategory_id: int, serial_number: int, session: Any) -> int:
        """Получение id транспорта по категории, подкатегории, серийному номеру"""
        try:
            row = await session.fetchval(
                """
                SELECT id
                FROM transports
                WHERE category_id = $1 AND subcategory_id = $2 AND serial_number = $3
                """,
                category_id, subcategory_id, serial_number
            )

            return row

        except Exception as e:
            logger.error(f"Ошибка при получении транспорта category_id: {category_id}, "
                         f"subcategory_id: {subcategory_id}, serial_number: {serial_number}: {e}")

    @staticmethod
    async def get_job_types_by_category(category_id: int, session: Any) -> List[Jobtype]:
        """Получение групп узлов (Jjobtypes) для категории"""
        try:
            rows = await session.fetch(
                """
                SELECT j.id, j.title, j.emoji
                FROM jobtypes j
                JOIN categories_jobtypes cj ON j.id = cj.jobtype_id 
                WHERE cj.category_id = $1
                """,
                category_id
            )

            jobtypes = [Jobtype.model_validate(row) for row in rows]
            return jobtypes
        except Exception as e:
            logger.error(f"Ошибка при получение групп узлов для категории {category_id}: {e}")

    @staticmethod
    async def get_jobtype_by_id(jobtype_id: int, session: Any) -> Jobtype:
        """Получение группы узлов по id"""
        try:
            row = await session.fetchrow(
                """
                SELECT *
                FROM jobtypes
                WHERE id = $1
                """,
                jobtype_id
            )

            return Jobtype.model_validate(row)
        except Exception as e:
            logger.error(f"Ошибка при получение групп узлов по id {jobtype_id}: {e}")

    @staticmethod
    async def get_all_jobs_by_jobtype_id(jobtype_id: int, session: Any) -> List[Job]:
        """Получение всех Job для jobtype"""
        try:
            rows = await session.fetch(
                """
                SELECT *
                FROM jobs
                WHERE jobtype_id = $1
                """,
                jobtype_id
            )

            jobs = [Job.model_validate(row) for row in rows]
            return jobs

        except Exception as e:
            logger.error(f"Ошибка при получении jobs для jobtype_id {jobtype_id}: {e}")

    @staticmethod
    async def get_jobs_by_ids(jobs_ids: List[int], session: Any) -> List[Job]:
        """Получение Job по списку id"""
        jobs_ids_list = f"({', '.join([str(job_id) for job_id in jobs_ids])})"
        try:
            rows = await session.fetch(
                f"""
                SELECT *
                FROM jobs
                WHERE id in {jobs_ids_list}
                """
            )

            jobs = [Job.model_validate(row) for row in rows]
            return jobs
        except Exception as e:
            logger.error(f"Получение работ по списку id {jobs_ids}: {e}")

    @staticmethod
    async def get_locations(session: Any) -> List[Location]:
        """Получение всех локаций"""
        try:
            rows = await session.fetch(
                """
                SELECT *
                FROM locations
                """
            )

            locations = [Location.model_validate(row) for row in rows]
            return locations

        except Exception as e:
            logger.error(f"Ошибка при получении всех локаций: {e}")

    @staticmethod
    async def create_operation(operation: OperationAdd, session: Any) -> None:
        """Создание операции"""
        try:
            await session.execute(
                """
                INSERT INTO operations (tg_id, transport_id, job_id, duration, location_id, comment, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                operation.tg_id, operation.transport_id, operation.job_id, operation.duration, operation.location_id,
                operation.comment, operation.created_at, operation.updated_at
            )
            logger.info(f"Записана операция пользователем {operation.tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании операции {operation}: {e}")

    @staticmethod
    async def get_operation_by_params(transport_id: int, job_id: int, location_id: int, session: Any) -> Operation | None:
        """Получение операции по параметрам, не позднее дня"""
        check_date = datetime.datetime.now() - datetime.timedelta(days=1)
        try:
            row = await session.fetchrow(
                """
                SELECT *
                FROM operations
                WHERE transport_id = $1 AND job_id = $2 AND location_id = $3 AND created_at > $4
                """,
                transport_id, job_id, location_id, check_date
            )
            if row:
                return Operation.model_validate(row)
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении операции за последний день по параметрам transport_id {transport_id} "
                         f"job_id {job_id} location_id {location_id}: {e}")