from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import crud
from filters.is_admin import IsAdmin
from keyboards.inline import admin_menu_kb, back_to_admin_kb

router = Router(name="admin_panel")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin:back")
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery) -> None:
    stats = await crud.get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"💬 Faol suhbatlar: {stats['active_chats']}\n"
        f"🔎 Qidiruvdagi foydalanuvchilar: {stats['searching']}\n"
        f"⛔️ Bloklangan foydalanuvchilar: {stats['banned_users']}\n"
        f"🔠 Taqiqlangan so'zlar soni: {stats['banned_words']}\n"
    )
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()
