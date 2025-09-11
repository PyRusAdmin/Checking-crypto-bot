# -*- coding: utf-8 -*-
from loguru import logger

from system.system import bot, UserSendMessage


async def send_transaction_alert(transaction_id, time, amount, symbol, from_transaction, to_transaction):
    """Отправляет уведомление о новой транзакции целевому пользователю"""
    for user_id in UserSendMessage:
        try:
            message_text = (
                f"💰 Новая транзакция!\n\n"
                f"• Сумма: {amount} {symbol}\n"
                f"• От: {from_transaction}\n"
                f"• Время: {time}\n"
                f"• Кошелек: {to_transaction}"
            )
            await bot.send_message(chat_id=user_id, text=message_text)
            logger.info(f"Уведомление отправлено пользователю {user_id} о транзакции {transaction_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление: {e}")
