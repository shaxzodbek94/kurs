from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import crud
from filters.is_admin import IsAdmin
from keyboards.inline import back_to_admin_kb, banned_words_menu_kb
from states import AdminStates

router = Router(name="admin_banned_words")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:banned_words")
async def banned_words_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🔠 <b>Taqiqlangan so'zlar bo'limi</b>", reply_markup=banned_words_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "bw:add")
async def ask_add_word(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Qo'shmoqchi bo'lgan so'zni kiriting:", reply_markup=back_to_admin_kb()
    )
    await state.set_state(AdminStates.add_banned_word)
    await callback.answer()


@router.message(AdminStates.add_banned_word)
async def add_word(message: Message, state: FSMContext) -> None:
    word = (message.text or "").strip().lower()
    await state.clear()
    if not word:
        await message.answer("Noto'g'ri so'z.")
        return

    added = await crud.add_banned_word(word)
    if added:
        await message.answer(f"✅ '{word}' taqiqlangan so'zlar ro'yxatiga qo'shildi.")
    else:
        await message.answer("Bu so'z allaqachon ro'yxatda mavjud.")


@router.callback_query(F.data == "bw:remove")
async def ask_remove_word(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "O'chirmoqchi bo'lgan so'zni kiriting:", reply_markup=back_to_admin_kb()
    )
    await state.set_state(AdminStates.remove_banned_word)
    await callback.answer()


@router.message(AdminStates.remove_banned_word)
async def remove_word(message: Message, state: FSMContext) -> None:
    word = (message.text or "").strip().lower()
    await state.clear()

    removed = await crud.remove_banned_word(word)
    if removed:
        await message.answer(f"✅ '{word}' ro'yxatdan o'chirildi.")
    else:
        await message.answer("Bu so'z ro'yxatda topilmadi.")


@router.callback_query(F.data == "bw:list")
async def list_words(callback: CallbackQuery) -> None:
    words = await crud.list_banned_words()
    if not words:
        text = "Taqiqlangan so'zlar ro'yxati bo'sh."
    else:
        text = "🔠 <b>Taqiqlangan so'zlar:</b>\n\n" + "\n".join(f"• {w}" for w in words)

    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()
