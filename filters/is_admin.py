from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from config import config


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if not event.from_user:
            return False
        return event.from_user.id in config.admin_ids
