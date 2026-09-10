from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import crud
from filters.is_admin import IsAdmin
from keyboards.inline import back_to_admin_kb
from states import AdminStates

router = Router(name="admin_users")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:ban_user")
async def ask_ban_user(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Bloklamoqchi bo'lgan foydalanuvchining Telegram ID sini kiriting:",
        reply_markup=back_to_admin_kb(),
    )
    await state.set_state(AdminStates.ban_user_id)
    await callback.answer()


@router.message(AdminStates.ban_user_id)
async def ban_user_by_id(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Noto'g'ri ID.")
        return

    user_id = int(text)
    user = await crud.get_user(user_id)
    if not user:
        await message.answer("Foydalanuvchi topilmadi.")
        return

    await crud.ban_user(user_id, "Administrator tomonidan bloklandi")
    await crud.end_chat(user_id)
    await message.answer(f"⛔️ Foydalanuvchi (id: {user_id}) bloklandi.")


@router.callback_query(F.data == "admin:unban_user")
async def ask_unban_user(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Blokdan chiqarmoqchi bo'lgan foydalanuvchining Telegram ID sini kiriting:",
        reply_markup=back_to_admin_kb(),
    )
    await state.set_state(AdminStates.unban_user_id)
    await callback.answer()


@router.message(AdminStates.unban_user_id)
async def unban_user_by_id(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Noto'g'ri ID.")
        return

    user_id = int(text)
    user = await crud.get_user(user_id)
    if not user:
        await message.answer("Foydalanuvchi topilmadi.")
        return

    await crud.unban_user(user_id)
    await message.answer(f"✅ Foydalanuvchi (id: {user_id}) blokdan chiqarildi.")


@router.callback_query(F.data == "admin:banned_list")
async def show_banned_list(callback: CallbackQuery) -> None:
    users = await crud.list_banned_users()
    if not users:
        text = "Bloklangan foydalanuvchilar yo'q."
    else:
        lines = [f"• {u.full_name} (id: {u.id}) — {u.ban_reason or '-'}" for u in users]
        text = "⛔️ <b>Bloklangan foydalanuvchilar:</b>\n\n" + "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()
