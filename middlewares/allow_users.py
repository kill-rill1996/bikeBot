from collections.abc import Awaitable, Callable
from typing import Any
from cache import r

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from settings import settings
from schemas.users import AllowUser


class AllowUsers(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["admin"] = self._check_user_access(event)
        return await handler(event, data)

    def _check_user_access(self, event: TelegramObject) -> bool:
        try:
            cached_data = r.smembers("allow_users")
            print(cached_data)
            print(type(cached_data))

            if cached_data:
                return str(event.from_user.id) in cached_data
            else:
                pass
        except Exception:
            return False