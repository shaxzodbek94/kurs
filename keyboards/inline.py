from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Statistika", callback_data="admin:stats")
    kb.button(text="📢 Xabar yuborish", callback_data="admin:broadcast")
    kb.button(text="🔠 Taqiqlangan so'zlar", callback_data="admin:banned_words")
    kb.button(text="🚫 Foydalanuvchini bloklash", callback_data="admin:ban_user")
    kb.button(text="✅ Blokdan chiqarish", callback_data="admin:unban_user")
    kb.button(text="📃 Bloklanganlar ro'yxati", callback_data="admin:banned_list")
    kb.adjust(1)
    return kb.as_markup()


def banned_words_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ So'z qo'shish", callback_data="bw:add")
    kb.button(text="➖ So'z o'chirish", callback_data="bw:remove")
    kb.button(text="📋 Ro'yxatni ko'rish", callback_data="bw:list")
    kb.button(text="⬅️ Orqaga", callback_data="admin:back")
    kb.adjust(1)
    return kb.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Orqaga", callback_data="admin:back")
    return kb.as_markup()
