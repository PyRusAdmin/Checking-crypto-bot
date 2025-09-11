# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram import F
from aiogram.types import CallbackQuery, Message
from loguru import logger

from database.database import read_from_db, write_database
from keyboards.keyboards import back, confirmation_keyboard
from parser.parser import fetch_tron_transactions
from system.system import WALLET, WALLET_1, router, bot, TARGET_USER_ID


async def send_long_message(message: Message, text: str, chunk_size: int = 4000):
    """Отправляем длинное сообщение по кускам"""
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i: i + chunk_size], reply_markup=back())


@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    """Регистрация пользователя"""
    logger.debug(
        f"ID: {query.from_user.id}, username: {query.from_user.username}, last_name: {query.from_user.last_name}, first_name: {query.from_user.first_name}"
    )
    """
    Запись в базу данных (database/people.db), данных пользователя, таких как: id, username, имя, фамилия, статус. 
    По умолчанию статус "False", так как нужно подтверждение регистрации от администратора телеграмм бота. 
    После подтверждения регистрации статус меняется на "True".
    """
    if query.from_user.id == TARGET_USER_ID:
        status = "True"
    else:
        status = "False"

    write_database(
        id_user=query.from_user.id,  # id пользователя
        user_name=query.from_user.username,  # username
        last_name=query.from_user.last_name,  # фамилия
        first_name=query.from_user.first_name,  # имя
        status=status  # статус по умолчанию "False"
    )
    # Сообщение самому пользователю
    await query.message.answer(
        text="✅ Регистрация пройдена. Ожидайте подтверждения от администратора.",
        reply_markup=back()
    )
    # await query.answer()  # убираем "часики" в Telegram

    # Сообщение админу
    await bot.send_message(
        chat_id=TARGET_USER_ID,
        text=f"Пользователь @{query.from_user.username or query.from_user.id} отправил данные для подтверждения регистрации.\n",
        reply_markup=confirmation_keyboard(query.from_user.id),
    )


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_user(query: CallbackQuery) -> None:
    """Подтверждение регистрации администратором бота"""
    target_id = int(query.data.split(":")[1])  # достаем id пользователя

    logger.debug(f"Подтверждение регистрации пользователя: {target_id}")

    write_database(
        id_user=target_id,  # меняем только id
        user_name=None,  # меняем только статус
        last_name=None,
        first_name=None,
        status="True"
    )

    await query.message.answer(f"✅ Пользователь {target_id} подтвержден.")


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
    router.callback_query.register(callback_today_transactions_handler)  # Загрузка транзакций за сегодня
    router.callback_query.register(confirm_user)  # Подтверждение регистрации
