# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message

from handler.handler import register_handler
from keyboards.keyboards import register_keyboard
from system.system import router, dp, bot


# Хендлер команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}!",
        reply_markup=register_keyboard()
    )


async def main() -> None:
    # Запускаем бота
    register_handler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
