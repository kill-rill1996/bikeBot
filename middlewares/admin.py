from collections.abc import Awaitable, Callable
from typing import Any
from cache import r

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from settings import settings


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["admin"] = self._check_admin_access(event)
        return await handler(event, data)

    def _check_admin_access(self, event: TelegramObject) -> bool:
        try:
            db_admins = r.get("admins").decode()
            admin_ids: list[str] = settings.admins + db_admins.split("|")
            return str(event.from_user.id) in admin_ids
        except Exception:
            return False
