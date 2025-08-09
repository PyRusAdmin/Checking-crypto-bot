from aiogram import F
from aiogram.types import CallbackQuery

from system.system import router


# Хендлер нажатия на кнопку "register"
@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    await query.message.answer("✅ Регистрация пройдена")
    await query.answer()  # Чтобы убрать "часики" в Telegram


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)
