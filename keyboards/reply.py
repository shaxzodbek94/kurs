from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔍 Suhbatdosh topish")
    kb.button(text="👤 Profilim")
    kb.button(text="ℹ️ Yordam")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def searching_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ Qidiruvni bekor qilish")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def chatting_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🛑 Suhbatni tugatish")
    kb.button(text="🚫 Foydalanuvchini bloklash")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def gender_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Erkak")
    kb.button(text="👩 Ayol")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def skip_photo_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="⏭ Rasmsiz davom etish")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ Bekor qilish")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
