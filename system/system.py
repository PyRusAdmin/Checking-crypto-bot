# -*- coding: utf-8 -*-
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from loguru import logger

# Загружаем переменные окружения из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")  # Получаем токен бота
WALLET = os.getenv("WALLET")  # Получаем кошелек пользователя
WALLET_1 = os.getenv("WALLET_1")  # Получаем кошелек пользователя

logger.debug(f"TOKEN: {TOKEN}, WALLET: {WALLET}, WALLET_1: {WALLET_1}")

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
