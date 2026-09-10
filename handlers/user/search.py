from aiogram import F, Router
from aiogram.types import Message

from database import crud
from database.models import UserState
from keyboards.reply import chatting_kb, main_menu_kb, searching_kb

router = Router(name="search")


@router.message(F.text == "🔍 Suhbatdosh topish")
async def start_search(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user:
        await message.answer("Avval ro'yxatdan o'ting: /start")
        return
    if user.is_banned:
        await message.answer("⛔️ Siz botdan foydalana olmaysiz.")
        return
    if user.state == UserState.CHATTING.value:
        await message.answer("Siz allaqachon suhbatdasiz.", reply_markup=chatting_kb())
        return
    if user.state == UserState.SEARCHING.value:
        await message.answer("Suhbatdosh qidirilmoqda... ⏳", reply_markup=searching_kb())
        return

    partner = await crud.find_waiting_partner(user.id)
    if partner is None:
        await crud.update_user_state(user.id, UserState.SEARCHING.value)
        await message.answer(
            "🔎 Suhbatdosh qidirilmoqda... Iltimos, kuting.",
            reply_markup=searching_kb(),
        )
        return

    await crud.pair_users(user.id, partner.id)
    await message.answer(
        "✅ Suhbatdosh topildi! Suhbatni boshlashingiz mumkin.",
        reply_markup=chatting_kb(),
    )
    try:
        await message.bot.send_message(
            partner.id,
            "✅ Suhbatdosh topildi! Suhbatni boshlashingiz mumkin.",
            reply_markup=chatting_kb(),
        )
    except Exception:
        pass


@router.message(F.text == "❌ Qidiruvni bekor qilish")
async def cancel_search(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user or user.state != UserState.SEARCHING.value:
        await message.answer("Siz hozircha qidiruvda emassiz.", reply_markup=main_menu_kb())
        return
    await crud.update_user_state(user.id, UserState.IDLE.value)
    await message.answer("Qidiruv bekor qilindi.", reply_markup=main_menu_kb())


@router.message(F.text == "🛑 Suhbatni tugatish")
async def stop_chat(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user or user.state != UserState.CHATTING.value:
        await message.answer("Siz hozircha suhbatda emassiz.", reply_markup=main_menu_kb())
        return

    partner_id = await crud.end_chat(user.id)
    await message.answer("Suhbat tugatildi.", reply_markup=main_menu_kb())
    if partner_id:
        try:
            await message.bot.send_message(
                partner_id,
                "Suhbatdoshingiz suhbatni tugatdi.",
                reply_markup=main_menu_kb(),
            )
        except Exception:
            pass
