from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database import crud
from keyboards.reply import gender_kb, main_menu_kb, skip_photo_kb
from states import Registration

router = Router(name="registration")


# --- cancel handlers must be registered first so they take priority over
# --- the generic state handlers below -------------------------------------


@router.message(StateFilter(Registration), Command("cancel"))
async def cancel_registration_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Ro'yxatdan o'tish bekor qilindi. Qayta boshlash uchun /start bosing.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(StateFilter(Registration), F.text == "❌ Bekor qilish")
async def cancel_registration_btn(message: Message, state: FSMContext) -> None:
    await cancel_registration_cmd(message, state)


# --- registration steps ----------------------------------------------------


@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name or len(name) > 64:
        await message.answer("Iltimos, to'g'ri ism kiriting (1-64 belgi).")
        return
    await state.update_data(full_name=name)
    await message.answer("Yoshingizni kiriting (masalan: 25):")
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not (14 <= int(text) <= 99):
        await message.answer("Iltimos, to'g'ri yosh kiriting (14-99).")
        return
    await state.update_data(age=int(text))
    await message.answer("Jinsingizni tanlang:", reply_markup=gender_kb())
    await state.set_state(Registration.gender)


@router.message(Registration.gender, F.text.in_({"👨 Erkak", "👩 Ayol"}))
async def process_gender(message: Message, state: FSMContext) -> None:
    gender = "male" if message.text == "👨 Erkak" else "female"
    await state.update_data(gender=gender)
    await message.answer(
        "Profilingiz uchun rasm yuboring (ixtiyoriy):",
        reply_markup=skip_photo_kb(),
    )
    await state.set_state(Registration.photo)


@router.message(Registration.gender)
async def process_gender_invalid(message: Message) -> None:
    await message.answer("Iltimos, tugmalardan birini tanlang.", reply_markup=gender_kb())


@router.message(Registration.photo, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    photo_file_id = message.photo[-1].file_id
    await _finish_registration(message, state, photo_file_id)


@router.message(Registration.photo, F.text == "⏭ Rasmsiz davom etish")
async def skip_photo(message: Message, state: FSMContext) -> None:
    await _finish_registration(message, state, None)


@router.message(Registration.photo)
async def process_photo_invalid(message: Message) -> None:
    await message.answer("Rasm yuboring yoki 'Rasmsiz davom etish' tugmasini bosing.")


async def _finish_registration(message: Message, state: FSMContext, photo_file_id: str | None) -> None:
    data = await state.get_data()
    await crud.create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data["full_name"],
        age=data["age"],
        gender=data["gender"],
        bio=None,
        photo_file_id=photo_file_id,
    )
    await state.clear()
    await message.answer(
        "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\nEndi suhbatdosh qidirishingiz mumkin.",
        reply_markup=main_menu_kb(),
    )
