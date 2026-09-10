import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.engine import init_db
from handlers.admin import banned_words as admin_banned_words
from handlers.admin import broadcast as admin_broadcast
from handlers.admin import panel as admin_panel
from handlers.admin import users_admin as admin_users
from handlers.user import block as user_block
from handlers.user import chat as user_chat
from handlers.user import profile as user_profile
from handlers.user import registration as user_registration
from handlers.user import search as user_search
from handlers.user import start as user_start
from middlewares.ban_middleware import BanMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini tekshiring.")

    await init_db()

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.outer_middleware(BanMiddleware())
    dp.callback_query.outer_middleware(BanMiddleware())

    # Admin routers first, so admin-only commands/callbacks are handled
    # before falling through to the general user routers.
    dp.include_router(admin_panel.router)
    dp.include_router(admin_broadcast.router)
    dp.include_router(admin_banned_words.router)
    dp.include_router(admin_users.router)

    dp.include_router(user_start.router)
    dp.include_router(user_registration.router)
    dp.include_router(user_profile.router)
    dp.include_router(user_search.router)
    dp.include_router(user_block.router)
    # Chat relay is the fallback for any remaining text/photo/video message,
    # so it must be included last.
    dp.include_router(user_chat.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
