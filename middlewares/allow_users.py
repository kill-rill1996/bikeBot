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
        if self._check_user_access(event):
            return await handler(event, data)

        await event.answer("You don't have access to this bot", show_alert=True)

    def _check_user_access(self, event: TelegramObject) -> bool:
        try:
            cached_data = r.get(f"allowed_users:{str(event.from_user.id)}")
            if cached_data:
                return True
            return False

        except Exception:
            return False