# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import subprocess
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from database.database import save_bot_user, is_user_exists, is_user_status
from handler.handler import register_handler
from keyboards.keyboards import main_keyboard, register_keyboard
from monitor_wallets.monitor_wallets import monitor_wallets
from system.system import router, dp, bot


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Отвечает на команду /start"""
    logger.info(f"Пользователь {message.from_user.id} {message.from_user.username} начал работу с ботом")
    await save_bot_user(message)  # Записываем пользователя, который запустил бота.
    # user = is_user_exists(id_user=message.from_user.id)

    if is_user_exists(id_user=message.from_user.id):
        print("Пользователь найден ✅")

        status = is_user_status(id_user=message.from_user.id)
        if status == "False":
            await bot.send_message(
                text="Дождитесь одобрения регистрации администратором",
                chat_id=message.chat.id,
                # reply_markup=register_keyboard()
            )
        else:
            await bot.send_message(
                text="Приветствуем в боте!",
                chat_id=message.chat.id,
                reply_markup=main_keyboard()
            )
    else:
        print("Пользователь отсутствует ❌")
        await bot.send_message(
            text="Для работы с ботом, нужно пройти небольшую регистрацию",
            chat_id=message.chat.id,
            reply_markup=register_keyboard()
        )


async def main() -> None:
    # Запускаем бота
    register_handler()
    await monitor_wallets()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    # asyncio.create_task(monitor_wallets())  # Запускаем фоновую задачу
