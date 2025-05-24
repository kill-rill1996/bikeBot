import asyncio
import asyncpg

import aiogram as io
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache import r

from database.database import async_engine
from database.tables import Base
from database.orm import AsyncOrm
from middlewares.allow_users import AllowUsers

from middlewares.database import DatabaseMiddleware
from middlewares.admin import AdminMiddleware
from middlewares.tg_ids import IdMiddleware

from routers import main_router
from routers.buttons import commands as cmd

from settings import settings

# from middlewares.admin import AdminMiddleware
# from handlers import main_router
# from handlers.buttons import commands as cmd
# from schedulers import scheduler as scheduler_funcs


async def set_commands(bot: io.Bot):
    """Перечень команд для бота"""
    commands = [
        BotCommand(command=f"{cmd.START[0]}", description=f"{cmd.START[1]}"),
        # BotCommand(command=f"{cmd.MENU[0]}", description=f"{cmd.MENU[1]}"),
        # BotCommand(command=f"{cmd.KEYS[0]}", description=f"{cmd.KEYS[1]}"),
        # BotCommand(command=f"{cmd.BALANCE[0]}", description=f"{cmd.BALANCE[1]}"),
        # BotCommand(command=f"{cmd.BUY[0]}", description=f"{cmd.BUY[1]}"),
        # BotCommand(command=f"{cmd.INVITE[0]}", description=f"{cmd.INVITE[1]}"),
        # BotCommand(command=f"{cmd.INSTRUCTION[0]}", description=f"{cmd.INSTRUCTION[1]}"),
        # BotCommand(command=f"{cmd.HELP[0]}", description=f"{cmd.HELP[1]}"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_description(bot: io.Bot):
    """Описание бота до запуска"""
    await bot.set_my_description(f"Какое то краткое описание бота")


async def start_bot() -> None:
    """Запуск бота"""
    bot = io.Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # COMMANDS
    await set_commands(bot)

    # DESCRIPTION
    await set_description(bot)

    storage = MemoryStorage()
    dp = io.Dispatcher(storage=storage)

    # SCHEDULER
    # scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # перевод закончившихся подписок в неактивные, удаление пробных, оплата реф. ссылок
    # scheduler.add_job(scheduler_funcs.run_every_hour, trigger="cron", year='*', month='*', day="*", hour="*", minute=0,
    #                   second=0, start_date=datetime.now(), kwargs={"bot": bot})

    # обновление трафика ключей каждые settings.paid_period
    # scheduler.add_job(scheduler_funcs.run_every_day, trigger="cron", year='*', month='*', day="*", hour=1, minute=10,
    #                   second=0, start_date=datetime.now(), kwargs={"bot": bot})

    # scheduler.start()

    # ROUTERS
    dp.include_router(main_router)

    # MIDDLEWARES
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())
    dp.message.middleware(AllowUsers())
    dp.callback_query.middleware(AllowUsers())
    dp.message.middleware(IdMiddleware())
    dp.callback_query.middleware(IdMiddleware())

    # TODO  dev version
    await init_models()

    # добавляем в кэш ids пользователей
    db_session = await asyncpg.connect(
        user=settings.db.postgres_user,
        host=settings.db.postgres_host,
        password=settings.db.postgres_password,
        port=settings.db.postgres_port,
        database=settings.db.postgres_db
    )
    allow_user_ids = await AsyncOrm.get_allow_users(session=db_session)
    for tg_id in allow_user_ids:
        r.set(f"allowed_users:{tg_id}", "allowed")

    await dp.start_polling(bot)


# TODO  dev version
async def init_models():
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(start_bot())
