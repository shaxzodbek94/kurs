import re

from sqlalchemy import select

from database.engine import async_session
from database.models import BannedWord, Block, MediaLog, User, UserState

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)


async def create_user(
    user_id: int,
    username: str | None,
    full_name: str,
    age: int,
    gender: str,
    bio: str | None,
    photo_file_id: str | None,
) -> User:
    async with async_session() as session:
        user = User(
            id=user_id,
            username=username,
            full_name=full_name,
            age=age,
            gender=gender,
            bio=bio,
            photo_file_id=photo_file_id,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_state(user_id: int, state: str, partner_id: int | None = None) -> None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.state = state
            user.partner_id = partner_id
            await session.commit()


async def get_all_user_ids() -> list[int]:
    async with async_session() as session:
        result = await session.execute(select(User.id))
        return [row[0] for row in result.all()]


async def get_stats() -> dict:
    async with async_session() as session:
        total_users = (await session.execute(select(User))).scalars().all()
        banned_words = (await session.execute(select(BannedWord))).scalars().all()

        active_chats = sum(1 for u in total_users if u.state == UserState.CHATTING.value) // 2
        searching = sum(1 for u in total_users if u.state == UserState.SEARCHING.value)
        banned_users = sum(1 for u in total_users if u.is_banned)

        return {
            "total_users": len(total_users),
            "active_chats": active_chats,
            "searching": searching,
            "banned_users": banned_users,
            "banned_words": len(banned_words),
        }


# ---------------------------------------------------------------------------
# Pairing / chat
# ---------------------------------------------------------------------------


async def find_waiting_partner(user_id: int) -> User | None:
    async with async_session() as session:
        blocked_by_me = {
            row[0]
            for row in (
                await session.execute(select(Block.blocked_id).where(Block.blocker_id == user_id))
            ).all()
        }
        blocked_me = {
            row[0]
            for row in (
                await session.execute(select(Block.blocker_id).where(Block.blocked_id == user_id))
            ).all()
        }
        excluded = blocked_by_me | blocked_me | {user_id}

        stmt = (
            select(User)
            .where(User.state == UserState.SEARCHING.value)
            .where(User.is_banned.is_(False))
            .where(User.id.not_in(excluded))
            .order_by(User.created_at.asc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def pair_users(user_id: int, partner_id: int) -> None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        partner = await session.get(User, partner_id)
        if user and partner:
            user.state = UserState.CHATTING.value
            user.partner_id = partner.id
            partner.state = UserState.CHATTING.value
            partner.partner_id = user.id
            await session.commit()


async def end_chat(user_id: int) -> int | None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return None
        partner_id = user.partner_id
        user.state = UserState.IDLE.value
        user.partner_id = None
        if partner_id:
            partner = await session.get(User, partner_id)
            if partner:
                partner.state = UserState.IDLE.value
                partner.partner_id = None
        await session.commit()
        return partner_id


# ---------------------------------------------------------------------------
# Blocking
# ---------------------------------------------------------------------------


async def block_user(blocker_id: int, blocked_id: int) -> None:
    async with async_session() as session:
        exists = await session.execute(
            select(Block).where(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
        )
        if exists.scalar_one_or_none():
            return
        session.add(Block(blocker_id=blocker_id, blocked_id=blocked_id))
        await session.commit()


async def ban_user(user_id: int, reason: str) -> None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.is_banned = True
            user.ban_reason = reason
            await session.commit()


async def unban_user(user_id: int) -> None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.is_banned = False
            user.ban_reason = None
            user.violations = 0
            await session.commit()


async def list_banned_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_banned.is_(True)))
        return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Banned words / violations
# ---------------------------------------------------------------------------


async def list_banned_words() -> list[str]:
    async with async_session() as session:
        result = await session.execute(select(BannedWord.word))
        return [row[0] for row in result.all()]


async def add_banned_word(word: str) -> bool:
    async with async_session() as session:
        exists = await session.execute(select(BannedWord).where(BannedWord.word == word))
        if exists.scalar_one_or_none():
            return False
        session.add(BannedWord(word=word))
        await session.commit()
        return True


async def remove_banned_word(word: str) -> bool:
    async with async_session() as session:
        result = await session.execute(select(BannedWord).where(BannedWord.word == word))
        banned_word = result.scalar_one_or_none()
        if not banned_word:
            return False
        await session.delete(banned_word)
        await session.commit()
        return True


async def find_banned_word(text: str) -> str | None:
    words = await list_banned_words()
    if not words:
        return None
    lowered = text.lower()
    tokens = set(re.findall(r"[\w']+", lowered, flags=re.UNICODE))
    for word in words:
        if word in tokens or word in lowered:
            return word
    return None


async def increment_violations(user_id: int) -> int:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return 0
        user.violations += 1
        await session.commit()
        return user.violations


# ---------------------------------------------------------------------------
# Media moderation log
# ---------------------------------------------------------------------------


async def log_media(sender_id: int, receiver_id: int, media_type: str, file_id: str) -> None:
    async with async_session() as session:
        session.add(
            MediaLog(
                sender_id=sender_id,
                receiver_id=receiver_id,
                media_type=media_type,
                file_id=file_id,
            )
        )
        await session.commit()
