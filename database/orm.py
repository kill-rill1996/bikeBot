import datetime
import asyncpg
from collections.abc import Mapping
from typing import Any, List

from logger import logger
from schemas.categories_and_jobs import Category, Subcategory, Jobtype, Job
from schemas.location import Location
from schemas.operations import Operation, OperationAdd, OperationJobs, OperationDetailJobs, OperationJob

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
    async def get_user_by_tg_id(tg_id: str, session: Any) -> User:
        """Получает пользователя"""
        try:
            row = await session.fetchrow(
                """
                SELECT * 
                FROM users
                WHERE tg_id = $1;
                """,
                tg_id
            )
            user = User.model_validate(row)
            return user

        except Exception as e:
            logger.error(f"Ошибка при получении пользователя {tg_id}: {e}")

    @staticmethod
    async def get_user_by_id(user_id: int, session: Any) -> User:
        """Получение пользователя по id"""
        try:
            row = await session.fetchrow(
                """
                SELECT * 
                FROM users
                WHERE id = $1 
                """,
                user_id
            )
            user = User.model_validate(row)
            return user

        except Exception as e:
            logger.error(f"Ошибка при получении пользователя id {user_id}: {e}")

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
    async def get_all_mechanics(session: Any) -> List[User]:
        """Получение всех механиков"""
        try:
            rows = await session.fetch(
                """
                SELECT id, tg_id, tg_username, username, created_at, role, lang
                FROM users
                WHERE role = 'mechanic' AND is_active = true
                ORDER BY username
                """
            )
            users = [User.model_validate(row) for row in rows]
            return users

        except Exception as e:
            logger.error(f"Ошибка при получении всех механиков: {e}")

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
            # создание operations
            operation_id = await session.fetchval(
                """
                INSERT INTO operations (tg_id, transport_id, duration, location_id, comment, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                operation.tg_id, operation.transport_id, operation.duration, operation.location_id,
                operation.comment, operation.created_at, operation.updated_at
            )

            # создание operations_jobs
            for job_id in operation.jobs_ids:
                await session.execute(
                    """
                    INSERT INTO operations_jobs (operation_id, job_id)
                    VALUES ($1, $2)
                    """,
                    operation_id, job_id
                )
            logger.info(f"Записана операция {operation_id} пользователем {operation.tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании операции {operation}: {e}")
            raise

    @staticmethod
    async def get_operation_by_params(transport_id: int, jobs_id: List[int], session: Any) -> List[Operation] | None:
        """Получение операции по параметрам, не позднее дня"""
        check_date = datetime.datetime.now() - datetime.timedelta(days=1)

        try:
            rows = await session.fetch(
                """
                SELECT o.*
                FROM operations AS o
                JOIN operations_jobs AS oj ON o.id = oj.operation_id
                WHERE o.transport_id = $1 AND o.created_at > $2 AND oj.job_id = ANY($3::int[])
                """,
                transport_id, check_date, jobs_id
            )
            if rows:
                return [Operation.model_validate(row) for row in rows]
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении операции за последний день по параметрам transport_id {transport_id} "
                         f"jobs_ids ({', '.join([str(job_id) for job_id in jobs_id])}): {e}")

    @staticmethod
    async def select_operations(start_period: datetime.datetime, end_period: datetime.datetime,
                                tg_id: str, session: Any) -> list[OperationJobs]:
        """Вывод операций за выбранный период"""
        try:
            # выбираем операции со всеми необходимыми компонентами
            rows = await session.fetch(
                """
                SELECT o.id, o.duration AS duration, t.serial_number, c.title AS transport_category, 
                sc.title AS transport_subcategory, o.created_at, j.title AS job_title
                FROM operations AS o
                JOIN transports AS t ON o.transport_id = t.id
                JOIN categories AS c ON t.category_id = c.id
                JOIN subcategories AS sc ON t.subcategory_id = sc.id
                JOIN operations_jobs AS oj ON o.id = oj.operation_id
                JOIN jobs AS j ON oj.job_id = j.id
                WHERE o.tg_id = $1 AND o.created_at >= $2 AND o.created_at <= $3
                ORDER BY o.created_at DESC
                """,
                tg_id, start_period, end_period
            )
            operations: list[OperationJob] = [OperationJob.model_validate(row) for row in rows]

            operations_jobs = {}
            for operation in operations:
                if operation.id in operations_jobs.keys():
                    operations_jobs[operation.id].append(operation.job_title)
                else:
                    operations_jobs[operation.id] = [operation.job_title]

            result = []
            for key, value in operations_jobs.items():
                for operation in operations:
                    if operation.id == key:
                        result.append(
                            OperationJobs(
                                id=operation.id,
                                duration=operation.duration,
                                serial_number=operation.serial_number,
                                transport_category=operation.transport_category,
                                transport_subcategory=operation.transport_subcategory,
                                created_at=operation.created_at,
                                jobs_titles=value,
                            )
                        )
                        break

            return sorted(result, key=lambda x: x.created_at, reverse=True)

        except Exception as e:
            logger.error(f"Ошибка при выборе списка операций за период {start_period} - {end_period} для пользователя {tg_id}: {e}")

    @staticmethod
    async def select_operation(operation_id: int, session: Any) -> OperationDetailJobs:
        """Вывод операций за выбранный период"""
        try:
            # получаем operations без jobs
            query = await session.fetchrow(
                """
                SELECT o.id, o.created_at, o.comment, o.duration, t.serial_number, c.title AS transport_category, 
                sc.title AS transport_subcategory 
                FROM operations AS o
                JOIN transports AS t ON o.transport_id = t.id
                JOIN categories AS c ON t.category_id = c.id
                JOIN subcategories AS sc ON t.subcategory_id = sc.id
                WHERE o.id = $1 
                """,
                operation_id
            )
            operation = OperationDetailJobs.model_validate(query)

            # получаем все jobs для операции
            try:
                rows = await session.fetch(
                    """
                    SELECT j.title AS title 
                    FROM operations_jobs AS oj
                    JOIN jobs AS j ON oj.job_id = j.id
                    WHERE oj.operation_id = $1
                    """,
                    operation.id
                )

                operation.jobs_titles = [row["title"] for row in rows]

            except Exception as e:
                logger.error(f"Ошибка при выборе работ для операции {operation.id}: {e}")

            return operation

        except Exception as e:
            logger.error(f"Ошибка при выборе операции id {operation_id}: {e}")

    @staticmethod
    async def get_operations_for_user_by_period(tg_id: str, period: str, session: Any) -> List[Operation]:
        """Получение операций за период для пользователя"""
        if period == "today":
            start_date = datetime.datetime.now() - datetime.timedelta(days=1)
            end_date = datetime.datetime.now()
        elif period == "yesterday":
            start_date = datetime.datetime.now() - datetime.timedelta(days=2)
            end_date = datetime.datetime.now() - datetime.timedelta(days=1)
        elif period == "week":
            start_date = datetime.datetime.now() - datetime.timedelta(weeks=1)
            end_date = datetime.datetime.now()
        elif period == "month":
            start_date = datetime.datetime.now() - datetime.timedelta(days=30)
            end_date = datetime.datetime.now()
        # TODO доделать произвольный период
        else:
            pass

        try:
            rows = await session.fetch(
                """
                SELECT *
                FROM operations
                WHERE tg_id = $1 AND created_at > $2 AND created_at < $3
                """,
                tg_id, start_date, end_date
            )
            operations = [Operation.model_validate(row) for row in rows]
            return operations

        except Exception as e:
            logger.error(f"Ошибка при получении операций пользователя {tg_id} с {start_date} до {end_date}: {e}")


    @staticmethod
    async def update_comment(operation_id: int, new_comment: str, session: Any) -> None:
        """Обновление комментария у сообщения"""
        try:
            await session.execute(
                """
                UPDATE operations SET comment=$1
                WHERE id=$2 
                """,
                new_comment, operation_id
            )

        except Exception as e:
            logger.error(f"Ошибка при обновлении комментария work id {operation_id}: {e}")

    @staticmethod
    async def delete_work(operation_id: int, session: Any) -> None:
        """Удаление работы"""
        try:
            async with session.transaction():
                # удаляем из таблицы связей operations_jobs
                await session.execute(
                    """
                    DELETE FROM operations_jobs WHERE operation_id=$1 
                    """,
                    operation_id
                )
                # удаляем из таблицы operations
                await session.execute(
                    """
                    DELETE FROM operations WHERE id=$1 
                    """,
                    operation_id
                )

        except Exception as e:
            logger.error(f"Ошибка при удалении работы operation_id {operation_id}: {e}")
            raise

    @staticmethod
    async def get_statistic_for_period(start_date: datetime.datetime, end_date: datetime.datetime,
                                       tg_id: str, session: Any) -> None:
        """Получение статистики по определенному периоду"""
        # SELECT
        # t.serial_number, c.title
        # AS
        # category, sc.title
        # AS
        # subcategory,
        # COUNT(*) as jobs_count, o.duration
        try:
            data = await session.fetch(
                """
                SELECT * 
                FROM operations AS o
                JOIN transports AS t ON o.transport_id = t.id
                JOIN categories AS c ON t.category_id = c.id
                JOIN subcategories AS sc ON t.subcategory_id = sc.id
                JOIN operations_jobs AS oj ON o.id = oj.operation_id
                JOIN jobs AS j ON oj.job_id = j.id
                """,
            )
            print(data)

        except Exception as e:
            logger.error(f"Ошибка при получении статистики для пользователя {tg_id} за период "
                         f"{start_date} - {end_date}: {e}")
