# -*- coding: utf-8 -*-
from loguru import logger

from system.system import bot, TARGET_USER_ID


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
