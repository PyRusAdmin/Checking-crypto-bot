# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message

from handler.handler import register_handler
from keyboards.keyboards import register_keyboard
from system.system import router, dp, bot, WALLET
import requests

# https://tronscan.org/

# GET https://apilist.tronscanapi.com/api/account/wallet?address=<ваш адрес>&asset_type=0

#GET https://apilist.tronscanapi.com/api/transfer/trx?address=<ваш адрес>&start=0&limit=20&direction=0

#GET https://apilist.tronscanapi.com/api/account/analysis?address=<ваш адрес>&type=0&start_timestamp=<ms>&end_timestamp=<ms>


def get_tron_balance(address: str):
    response = requests.get(f"https://apilist.tronscanapi.com/api/account/wallet?address={address}&asset_type=0")
    print(response.status_code)  # Выводит статус-код ответа
    print(response.json())  # Выводит JSON-ответ

    response = requests.get(f"https://apilist.tronscanapi.com/api/transfer/trx?address={address}&start=0&limit=20&direction=0")
    print(response.status_code)  # Выводит статус-код ответа
    print(response.json())  # Выводит JSON-ответ

    response = requests.get(
        f"https://apilist.tronscanapi.com/api/account/analysis?address={address}&type=0&start_timestamp=<ms>&end_timestamp=<ms>")
    print(response.status_code)  # Выводит статус-код ответа
    print(response.json())  # Выводит JSON-ответ


# Хендлер команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    get_tron_balance(address=WALLET)

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
