# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from handler.greeting import register_greeting_handler
from handler.handler import register_handler
from system.system import dp, bot


async def main() -> None:
    # Запускаем бота
    register_handler()

    register_greeting_handler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
