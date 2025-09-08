import asyncio
import datetime as dt
from datetime import datetime

import requests
from aiogram import F
from aiogram.types import CallbackQuery, Message
from loguru import logger
from peewee import IntegrityError

from database.database import read_from_db, Transactions, write_database
from keyboards.keyboards import back, main_keyboard, confirmation_keyboard
from system.system import WALLET, WALLET_1, router, bot


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


TARGET_USER_ID = 535185511  # ID пользователя, которому слать уведомления


async def send_transaction_alert(transaction_id, time, amount, symbol, from_transaction, to_transaction):
    """Отправляет уведомление о новой транзакции целевому пользователю"""
    try:
        message_text = (
            f"💰 Новая транзакция!\n\n"
            f"• Сумма: {amount} {symbol}\n"
            f"• От: {from_transaction}\n"
            f"• Время: {time}\n"
            f"• Кошелек: {to_transaction}"
        )
        await bot.send_message(chat_id=TARGET_USER_ID, text=message_text)
        logger.info(f"Уведомление отправлено пользователю {TARGET_USER_ID} о транзакции {transaction_id}")
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление: {e}")


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
        await asyncio.sleep(60)  # Ждём 60 секунд


async def fetch_tron_transactions(address: str) -> list:
    """Получает список новых (ещё не записанных в БД) транзакций для адреса"""
    result = [f"Транзакции USDT TRC20: {address}\n"]
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"  # УБРАЛ ПРОБЕЛЫ!
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


async def send_long_message(message: Message, text: str, chunk_size: int = 4000):
    """Отправляем длинное сообщение по кускам"""
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i: i + chunk_size], reply_markup=back())


@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    logger.debug(
        f"ID: {query.from_user.id}, username: {query.from_user.username}, last_name: {query.from_user.last_name}, first_name: {query.from_user.first_name}"
    )

    write_database(
        id_user=query.from_user.id,
        user_name=query.from_user.username,
        last_name=query.from_user.last_name,
        first_name=query.from_user.first_name,
        status="False"
    )
    # Сообщение самому пользователю
    await query.message.answer("✅ Регистрация пройдена. Ожидайте подтверждения от администратора.",
                               reply_markup=back())  # <-- добавил сюда кнопку назад)
    await query.answer()  # убираем "часики" в Telegram

    # Сообщение админу
    await bot.send_message(
        TARGET_USER_ID,
        f"Пользователь @{query.from_user.username or query.from_user.id} "
        f"отправил данные для подтверждения",
        reply_markup=confirmation_keyboard(),
    )


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_user(query: CallbackQuery) -> None:
    target_id = int(query.data.split(":")[1])  # достаем id пользователя

    write_database(
        id_user=target_id,
        user_name=None,  # меняем только статус
        last_name=None,
        first_name=None,
        status="True"
    )

    await query.message.answer(f"✅ Пользователь {target_id} подтвержден.")


@router.callback_query(F.data == "back")
async def callback_back_handler(query: CallbackQuery) -> None:
    """Выводит главное меню бота"""
    await query.message.answer(text="Приветствуем в боте!", reply_markup=main_keyboard())


@router.callback_query(F.data == "transactions")
async def callback_transactions_handler(query: CallbackQuery) -> None:
    wallet_addresses = [WALLET, WALLET_1]
    full_message_parts = []

    for address in wallet_addresses:
        try:
            transactions_text = await fetch_tron_transactions(address)
            full_message_parts.append(transactions_text)
        except Exception as e:
            logger.error(f"Ошибка при получении транзакций для {address}: {e}")
            full_message_parts.append(f"❌ Ошибка при загрузке транзакций для {address}")

    # Объединяем всё в одно сообщение
    full_message = "\n\n".join(full_message_parts)

    # Отправляем единое сообщение (или разбиваем, если оно слишком длинное)
    await send_long_message(query.message, full_message)


@router.callback_query(F.data == "today_transactions")
async def callback_today_transactions_handler(query: CallbackQuery) -> None:
    """Выводит транзакции за сегодня"""

    await query.message.answer("⏳ Загрузка...", reply_markup=back())

    rows = await read_from_db()

    today = datetime.now().date()
    today_transactions = []

    for row in rows:
        # Приводим row.time к дате
        if isinstance(row.time, datetime):
            transaction_date = row.time.date()
        elif isinstance(row.time, str):
            transaction_date = datetime.strptime(row.time[:10], "%Y-%m-%d").date()
        else:
            continue

        if transaction_date == today:
            today_transactions.append(row)

    # Формируем ответ
    if today_transactions:
        response = "📌 Транзакции за сегодня:\n\n"
        for t in today_transactions:
            amount = getattr(t, 'amount', 0.0)
            symbol = getattr(t, 'symbol', '???')  # <-- ИСПРАВЛЕНО: было currency → теперь symbol
            # Форматируем время
            if isinstance(t.time, datetime):
                time_str = t.time.strftime("%H:%M")
            elif isinstance(t.time, str) and ' ' in t.time:
                time_str = t.time.split()[1]
            else:
                time_str = "???"

            response += f"• {amount:.2f} {symbol} — {time_str}\n"
        await query.message.answer(response, reply_markup=back())
    else:
        await query.message.answer("📭 Сегодня транзакций нет.", reply_markup=back())


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)  # Регистрация
    router.callback_query.register(callback_transactions_handler)  # Отправка транзакций
    router.callback_query.register(callback_back_handler)  # Отправка главного меню
    router.callback_query.register(callback_today_transactions_handler)  # Загрузка транзакций за сегодня
    router.callback_query.register(confirm_user) # Подтверждение регистрации
