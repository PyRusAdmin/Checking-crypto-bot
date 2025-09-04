# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram.filters import CommandStart
from aiogram.types import Message

from handler.handler import register_handler
from keyboards.keyboards import main_keyboard
from system.system import router, dp, bot


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await bot.send_message(text="Приветствуем в боте!",
                           chat_id=message.chat.id, reply_markup=main_keyboard())


async def main() -> None:
    # Запускаем бота
    register_handler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
