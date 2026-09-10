from aiogram import F, Router
from aiogram.types import Message

from config import config
from database import crud
from database.models import UserState

router = Router(name="chat_relay")


async def _forward_media_to_admins(
    message: Message, sender, receiver_id: int, media_type: str, file_id: str
) -> None:
    await crud.log_media(sender.id, receiver_id, media_type, file_id)

    caption = (
        f"📎 Foydalanuvchilar orasida almashilgan {media_type}\n"
        f"Yuboruvchi: {sender.full_name} (id: {sender.id}, @{sender.username or '-'})\n"
        f"Qabul qiluvchi ID: {receiver_id}"
    )
    for admin_id in config.admin_ids:
        try:
            if media_type == "photo":
                await message.bot.send_photo(admin_id, file_id, caption=caption)
            else:
                await message.bot.send_video(admin_id, file_id, caption=caption)
        except Exception:
            pass


@router.message(F.content_type.in_({"photo", "video"}))
async def relay_media(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user or user.state != UserState.CHATTING.value or not user.partner_id:
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    else:
        file_id = message.video.file_id
        media_type = "video"

    try:
        if media_type == "photo":
            await message.bot.send_photo(user.partner_id, file_id, caption=message.caption)
        else:
            await message.bot.send_video(user.partner_id, file_id, caption=message.caption)
    except Exception:
        await message.answer("Xabar yuborilmadi. Suhbatdosh botni bloklagan bo'lishi mumkin.")
        return

    await _forward_media_to_admins(message, user, user.partner_id, media_type, file_id)


@router.message(F.text)
async def relay_text(message: Message) -> None:
    if message.text.startswith("/"):
        return

    user = await crud.get_user(message.from_user.id)
    if not user or user.state != UserState.CHATTING.value or not user.partner_id:
        return

    banned_word = await crud.find_banned_word(message.text)
    if banned_word:
        violations = await crud.increment_violations(user.id)
        await message.answer(
            "⚠️ Xabaringizda taqiqlangan so'z aniqlandi va u suhbatdoshga yuborilmadi.\n"
            f"Ogohlantirishlar soni: {violations}/{config.max_violations}"
        )

        if violations >= config.max_violations:
            await crud.ban_user(user.id, "Taqiqlangan so'zlarni takroriy ishlatish")
            partner_id = await crud.end_chat(user.id)
            await message.answer("⛔️ Siz qoidabuzarlik uchun botdan foydalanish huquqidan mahrum qilindingiz.")

            for admin_id in config.admin_ids:
                try:
                    await message.bot.send_message(
                        admin_id,
                        "🚫 Foydalanuvchi avtomatik bloklandi.\n"
                        f"Foydalanuvchi: {user.full_name} (id: {user.id})\n"
                        "Sabab: taqiqlangan so'zlarni takroriy ishlatish",
                    )
                except Exception:
                    pass

            if partner_id:
                try:
                    await message.bot.send_message(partner_id, "Suhbatdoshingiz suhbatni tark etdi.")
                except Exception:
                    pass
        return

    try:
        await message.bot.send_message(user.partner_id, message.text)
    except Exception:
        await message.answer("Xabar yuborilmadi. Suhbatdosh botni bloklagan bo'lishi mumkin.")
