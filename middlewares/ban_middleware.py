from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database import crud


class BanMiddleware(BaseMiddleware):
    """Blocks any interaction from a banned user, except /start."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is not None:
            user = await crud.get_user(tg_user.id)
            if user and user.is_banned:
                is_start_command = (
                    isinstance(event, Message) and event.text and event.text.startswith("/start")
                )
                if not is_start_command:
                    if isinstance(event, Message):
                        await event.answer(
                            "⛔️ Siz botdan foydalanish huquqidan mahrum qilingansiz.\n"
                            f"Sabab: {user.ban_reason or 'koʼrsatilmagan'}"
                        )
                    return None
        return await handler(event, data)
