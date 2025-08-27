# -*- coding: utf-8 -*-
import asyncio
import datetime as dt
import logging
import sys

import requests
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from handler.handler import register_handler
from system.system import router, dp, bot, WALLET, WALLET_1
from working_database.working_database import write_transaction


def get_tron_balance(address: str) -> str:
    """Получаем транзакции и возвращаем как строку для отправки в бота"""
    result = [f"Транзакции USDT TRC20: {address}\n"]

    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    pages = 3
    params = {
        'only_confirmed': True,
        'limit': 20,
    }

    for _ in range(pages):
        r = requests.get(url, params=params, headers={"accept": "application/json"})
        logger.info(r.json())

        params['fingerprint'] = r.json().get('meta', {}).get('fingerprint')

        for tr in r.json().get('data', []):
            to_transaction = tr.get('to')
            if to_transaction == address:
                symbol = tr.get('token_info', {}).get('symbol')
                value = tr.get('value', '')
                dec = -1 * int(tr.get('token_info', {}).get('decimals', '6'))
                amount = float(value[:dec] + '.' + value[dec:])
                logger.info(f"Найден перевод USDT по адресу {address} на сумму {amount} ")
                from_transaction = tr.get('from')
                time = dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000)
                result.append(f"{time} | {amount:>9.02f} {symbol} | {from_transaction} > {to_transaction}")
                tx_id = tr.get('transaction_id')
                write_transaction(tx_id, time, amount, symbol, from_transaction, to_transaction)

    return "\n".join(result)


async def send_long_message(message: Message, text: str, chunk_size: int = 4000):
    """Отправляем длинное сообщение по кускам"""
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i:i + chunk_size])


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    wallet = [WALLET, WALLET_1]

    for wall in wallet:
        transactions = get_tron_balance(address=wall)
        await send_long_message(message, transactions)  # отправляем кусками


async def main() -> None:
    # Запускаем бота
    register_handler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
