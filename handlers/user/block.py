from aiogram import F, Router
from aiogram.types import Message

from database import crud
from database.models import UserState
from keyboards.reply import main_menu_kb

router = Router(name="block")


@router.message(F.text == "🚫 Foydalanuvchini bloklash")
async def block_partner(message: Message) -> None:
    user = await crud.get_user(message.from_user.id)
    if not user or user.state != UserState.CHATTING.value or not user.partner_id:
        await message.answer("Siz hozircha suhbatda emassiz.", reply_markup=main_menu_kb())
        return

    partner_id = user.partner_id
    await crud.block_user(user.id, partner_id)
    await crud.end_chat(user.id)
    await message.answer(
        "🚫 Foydalanuvchi bloklandi. Endi u siz bilan bog'lana olmaydi.",
        reply_markup=main_menu_kb(),
    )
    try:
        await message.bot.send_message(
            partner_id,
            "Suhbatdoshingiz suhbatni tugatdi.",
            reply_markup=main_menu_kb(),
        )
    except Exception:
        pass
