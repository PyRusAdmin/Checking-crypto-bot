# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, Router, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from keyboards.keyboards import register_keyboard

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен бота
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Укажите его в .env или переменной окружения.")

# Создаём роутер
router = Router()

# Хендлер команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}!",
        reply_markup=register_keyboard()
    )

# Хендлер нажатия на кнопку "register"
@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    await query.message.answer("✅ Регистрация пройдена")
    await query.answer()  # Чтобы убрать "часики" в Telegram

async def main() -> None:
    # Создаём бота
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(router)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
