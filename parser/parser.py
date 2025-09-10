# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import requests
from loguru import logger
from peewee import IntegrityError

from database.database import Transactions
from handler.sending_message import send_transaction_alert
from system.system import WALLET, WALLET_1


async def write_transaction(transaction_id, time, amount, symbol, from_transaction, to_transaction):
    try:
        Transactions.create(
            transaction_id=transaction_id,
            time=time,
            amount=amount,
            symbol=symbol,
            from_transaction=from_transaction,
            to_transaction=to_transaction,
        )
        await send_transaction_alert(transaction_id, time, amount, symbol, from_transaction, to_transaction)
    except IntegrityError:
        logger.info(f"Транзакция {transaction_id} уже существует, пропускаем")


async def fetch_tron_transactions(address: str) -> list:
    """Получает список новых (ещё не записанных в БД) транзакций для адреса"""
    result = [f"Транзакции USDT TRC20: {address}\n"]
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    pages = 1
    params = {
        "only_confirmed": True,
        "limit": 20,
    }
    for _ in range(pages):
        r = requests.get(url, params=params, headers={"accept": "application/json"})
        logger.info(r.json())
        params["fingerprint"] = r.json().get("meta", {}).get("fingerprint")

        for tr in r.json().get("data", []):
            to_transaction = tr.get("to")
            from_transaction = tr.get("from")

            if to_transaction and to_transaction.lower() == address.lower():
                symbol = tr.get("token_info", {}).get("symbol")
                value = tr.get("value", "")
                dec = -1 * int(tr.get("token_info", {}).get("decimals", "6"))
                amount = float(value[:dec] + "." + value[dec:])
                time = dt.datetime.fromtimestamp(float(tr.get("block_timestamp", 0)) / 1000)
                result.append(f"{time} | {amount:>9.02f} {symbol} | от {from_transaction}")
                tx_id = tr.get("transaction_id")
                await write_transaction(tx_id, time, amount, symbol, from_transaction, to_transaction)
                logger.info(f"Новая транзакция записана: {tx_id}")

    return "\n".join(result)


async def monitor_wallets():
    """Фоновая задача: проверяет кошельки каждую минуту и отправляет уведомления о новых транзакциях"""
    wallets = [WALLET, WALLET_1]

    while True:
        try:
            for address in wallets:
                logger.info(f"Проверка кошелька: {address}")
                await fetch_tron_transactions(address)
        except Exception as e:
            logger.error(f"Ошибка в фоновой задаче: {e}")
        await asyncio.sleep(2 * 60)  # Ждём 60 секунд


if __name__ == "__main__":
    asyncio.run(monitor_wallets())
