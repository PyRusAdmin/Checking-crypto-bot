# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dotenv import load_dotenv
load_dotenv()  # Загружаем переменные из .env


# Получаем токен бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Укажите его в переменной окружения.")

# Создаём роутер для обработки команд
router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

async def main() -> None:
    # Инициализация бота
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем роутер
    dp.include_router(router)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
