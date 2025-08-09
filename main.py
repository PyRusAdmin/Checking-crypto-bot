# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
from datetime import datetime

import requests
from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message

from handler.handler import register_handler
from keyboards.keyboards import register_keyboard
from system.system import router, dp, bot, WALLET


# https://tronscan.org/

# GET https://apilist.tronscanapi.com/api/account/wallet?address=<ваш адрес>&asset_type=0

# GET https://apilist.tronscanapi.com/api/transfer/trx?address=<ваш адрес>&start=0&limit=20&direction=0

# GET https://apilist.tronscanapi.com/api/account/analysis?address=<ваш адрес>&type=0&start_timestamp=<ms>&end_timestamp=<ms>


def get_tron_balance(address: str):
    # Баланс
    balance_resp = requests.get(
        f"https://apilist.tronscanapi.com/api/account/wallet?address={address}&asset_type=0"
    ).json()

    print("\n=== Баланс ===")
    for token in balance_resp.get("data", []):
        print(f"{token['token_name'].upper()} ({token['token_abbr']}): "
              f"{token['balance']} "
              f"~ {token['token_value_in_usd']}$")

    # Последние транзакции
    tx_resp = requests.get(
        f"https://apilist.tronscanapi.com/api/transfer/trx?address={address}&start=0&limit=5&direction=0"
    ).json()

    print("\n=== Последние транзакции ===")
    for tx in tx_resp.get("data", []):
        ts = datetime.fromtimestamp(tx['block_timestamp'] / 1000)
        direction = "Вход" if tx['direction'] == 2 else "Выход"
        print(f"{ts} | {direction} | {tx['amount']} TRX "
              f"от {tx['from']} -> {tx['to']}")

    # Анализ по дням
    analysis_resp = requests.get(
        f"https://apilist.tronscanapi.com/api/account/analysis"
        f"?address={address}&type=0&start_timestamp=0&end_timestamp=9999999999999"
    ).json()

    print("\n=== Дневная статистика ===")
    for day in analysis_resp.get("data", [])[:10]:
        print(f"{day['day']}: {day['trx_amount']} TRX "
              f"({day['usdt_amount']} USDT), цена {day['price']}$")


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
