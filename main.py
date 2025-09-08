# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from database.database import save_bot_user
from handler.handler import register_handler, monitor_wallets
from keyboards.keyboards import main_keyboard
from system.system import router, dp, bot


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Отвечает на команду /start"""
    logger.info(f"Пользователь {message.from_user.id} {message.from_user.username} начал работу с ботом")
    await save_bot_user(message)

    await bot.send_message(text="Приветствуем в боте!",
                           chat_id=message.chat.id, reply_markup=main_keyboard())

    # Запускаем фоновую задачу
    await asyncio.create_task(monitor_wallets())


async def main() -> None:
    # Запускаем бота
    register_handler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
