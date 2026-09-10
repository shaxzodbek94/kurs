from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import crud
from keyboards.reply import cancel_kb, main_menu_kb
from states import Registration

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await crud.get_user(message.from_user.id)

    if user:
        if user.is_banned:
            await message.answer(
                "⛔️ Siz botdan foydalanish huquqidan mahrum qilingansiz.\n"
                f"Sabab: {user.ban_reason or 'koʼrsatilmagan'}"
            )
            return
        await message.answer(
            f"Xush kelibsiz, {user.full_name}! 👋",
            reply_markup=main_menu_kb(),
        )
        return

    await message.answer(
        "🌹 <b>Tanishuv botiga xush kelibsiz!</b>\n\n"
        "Bu yerda siz tasodifiy suhbatdosh bilan anonim tarzda tanishishingiz mumkin.\n\n"
        "Ro'yxatdan o'tish uchun ismingizni kiriting:",
        reply_markup=cancel_kb(),
    )
    await state.set_state(Registration.name)
