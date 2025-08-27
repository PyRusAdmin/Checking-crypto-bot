# -*- coding: utf-8 -*-
import asyncio
import datetime as dt
import logging
import sys

import requests
from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message

from handler.handler import register_handler
from keyboards.keyboards import register_keyboard
from system.system import router, dp, bot, WALLET, WALLET_1


def get_tron_balance(address: str):
    print("Транзакции USDT TRC20: TXtncqF1R75QAdmMAQCYEds2VDv13z2hM8")

    num = 0
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    pages = 3

    params = {
        'only_confirmed': True,
        'limit': 20,
    }

    for _ in range(0, pages):
        r = requests.get(url, params=params, headers={"accept": "application/json"})
        params['fingerprint'] = r.json().get('meta', {}).get('fingerprint')

        for tr in r.json().get('data', []):
            num += 1
            symbol = tr.get('token_info', {}).get('symbol')
            fr = tr.get('from')
            to = tr.get('to')
            v = tr.get('value', '')
            dec = -1 * int(tr.get('token_info', {}).get('decimals', '6'))
            f = float(v[:dec] + '.' + v[dec:])
            time_ = dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000)

            print(f"{num:>3} | {time_} | {f:>9.02f} {symbol} | {fr} > {to}")


# Хендлер команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    wallet = [WALLET, WALLET_1]
    for wall in wallet:
        get_tron_balance(address=wall)
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
