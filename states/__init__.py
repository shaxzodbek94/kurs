from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    photo = State()


class AdminStates(StatesGroup):
    broadcast_message = State()
    add_banned_word = State()
    remove_banned_word = State()
    ban_user_id = State()
    unban_user_id = State()
