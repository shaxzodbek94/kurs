from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import crud
from filters.is_admin import IsAdmin
from keyboards.inline import back_to_admin_kb
from states import AdminStates

router = Router(name="admin_broadcast")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:broadcast")
async def ask_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting "
        "(matn, rasm yoki video bo'lishi mumkin):",
        reply_markup=back_to_admin_kb(),
    )
    await state.set_state(AdminStates.broadcast_message)
    await callback.answer()


@router.message(AdminStates.broadcast_message)
async def send_broadcast(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_ids = await crud.get_all_user_ids()

    sent, failed = 0, 0
    for user_id in user_ids:
        try:
            await message.copy_to(user_id)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Xabar yuborildi.\nMuvaffaqiyatli: {sent}\nXatolik: {failed}")
