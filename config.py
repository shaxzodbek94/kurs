import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",") if x.strip()]


@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: list[int] = field(default_factory=lambda: _parse_admin_ids(os.getenv("ADMIN_IDS", "")))
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
    max_violations: int = int(os.getenv("MAX_VIOLATIONS", "5"))


config = Config()
