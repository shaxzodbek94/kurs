from aiogram import F, Router
from aiogram.types import Message

from database import crud

router = Router(name="profile")

GENDER_LABELS = {"male": "👨 Erkak", "female": "👩 Ayol"}


@router.message(F.text == "👤 Profilim")
async def show_profile(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user:
        await message.answer("Avval ro'yxatdan o'ting: /start")
        return

    caption = (
        f"👤 <b>{user.full_name}</b>\n"
        f"🎂 Yosh: {user.age}\n"
        f"⚧ Jins: {GENDER_LABELS.get(user.gender, user.gender)}\n"
    )
    if user.photo_file_id:
        await message.answer_photo(user.photo_file_id, caption=caption)
    else:
        await message.answer(caption)


@router.message(F.text == "ℹ️ Yordam")
async def show_help(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "🔍 <b>Suhbatdosh topish</b> — tasodifiy suhbatdosh bilan bog'lanish\n"
        "🛑 <b>Suhbatni tugatish</b> — joriy suhbatni yakunlash\n"
        "🚫 <b>Foydalanuvchini bloklash</b> — suhbatdoshni bloklash "
        "(u bilan qayta bog'lana olmaysiz)\n"
        "👤 <b>Profilim</b> — profilingizni ko'rish\n\n"
        "⚠️ Taqiqlangan so'zlarni ishlatish man etiladi va botdan "
        "foydalanish huquqidan mahrum bo'lishga olib kelishi mumkin."
    )
