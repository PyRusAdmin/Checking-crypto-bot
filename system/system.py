# -*- coding: utf-8 -*-
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from loguru import logger

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен бота
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Укажите его в .env или переменной окружения.")
#  Получаем кошелек пользователя
WALLET = os.getenv("WALLET")
if not WALLET:
    raise ValueError("❌ WALLET не найден! Укажите его в .env или переменной окружения.")

logger.debug(f"TOKEN: {TOKEN}, WALLET: {WALLET}")

# Создаём роутер
router = Router()

# Создаём бота
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(router)
