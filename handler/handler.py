import datetime as dt
import requests
from aiogram import F
from aiogram.types import CallbackQuery, Message
from loguru import logger

from keyboards.keyboards import back, main_keyboard
from system.system import WALLET, WALLET_1, router
from working_database.working_database import write_transaction


def get_tron_balance(address: str) -> str:
    """Получаем транзакции и возвращаем как строку для отправки в бота"""
    result = [f"Транзакции USDT TRC20: {address}\n"]

    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    pages = 3
    params = {
        "only_confirmed": True,
        "limit": 20,
    }

    for _ in range(pages):
        r = requests.get(url, params=params, headers={
                         "accept": "application/json"})
        logger.info(r.json())

        params["fingerprint"] = r.json().get("meta", {}).get("fingerprint")

        # оставляем только входящие транзакции
        for tr in r.json().get("data", []):
            to_transaction = tr.get("to")
            from_transaction = tr.get("from")

            if to_transaction and to_transaction.lower() == address.lower():
                symbol = tr.get("token_info", {}).get("symbol")
                value = tr.get("value", "")
                dec = -1 * int(tr.get("token_info", {}).get("decimals", "6"))
                amount = float(value[:dec] + "." + value[dec:])

                time = dt.datetime.fromtimestamp(
                    float(tr.get("block_timestamp", 0)) / 1000
                )
                result.append(
                    f"{time} | {amount:>9.02f} {symbol} | от {from_transaction}"
                )

                tx_id = tr.get("transaction_id")
                write_transaction(
                    tx_id, time, amount, symbol, from_transaction, to_transaction
                )

    return "\n".join(result)


async def send_long_message(message: Message, text: str, chunk_size: int = 4000):
    """Отправляем длинное сообщение по кускам"""
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i: i + chunk_size], reply_markup=back())


@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    id_user = query.from_user.id
    user_name = query.from_user.username
    last_name = query.from_user.last_name
    first_name = query.from_user.first_name

    logger.debug(
        f"ID: {id_user}, username: {user_name}, last_name: {last_name}, first_name: {first_name}"
    )

    # если нужен write_database, оставь его вместо write_transaction
    write_transaction(id_user, user_name, last_name, first_name)

    await query.message.answer("✅ Регистрация пройдена",
                               reply_markup=back())   # <-- добавил сюда кнопку назад)
    await query.answer()  # убираем "часики" в Telegram


@router.callback_query(F.data == "back")
async def callback_back_handler(query: CallbackQuery) -> None:
    """Выводит главное меню бота"""
    await query.message.answer(text="Приветствуем в боте!", reply_markup=main_keyboard())


@router.callback_query(F.data == "transactions")
async def callback_transactions_handler(query: CallbackQuery) -> None:
    wallet = [WALLET, WALLET_1]

    for wall in wallet:
        transactions = get_tron_balance(address=wall)
        # исправил message → query.message
        await send_long_message(query.message, transactions)


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)
    router.callback_query.register(callback_transactions_handler)
    router.callback_query.register(callback_back_handler)
