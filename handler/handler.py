from aiogram import F
from aiogram.types import CallbackQuery
from loguru import logger

from system.system import router
from working_database.working_database import write_database


@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    id_user = query.from_user.id
    user_name = query.from_user.username
    last_name = query.from_user.last_name
    first_name = query.from_user.first_name

    logger.debug(
        f"ID: {id_user}, username: {user_name}, last_name: {last_name}, first_name: {first_name}"
    )

    write_database(id_user, user_name, last_name, first_name)

    await query.message.answer("✅ Регистрация пройдена")
    await query.answer()  # Убираем "часики" в Telegram


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)
