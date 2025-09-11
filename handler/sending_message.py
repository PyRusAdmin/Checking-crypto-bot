# -*- coding: utf-8 -*-
from loguru import logger

from database.database import Users
from system.system import bot


async def send_transaction_alert(transaction_id, time, amount, symbol, from_transaction, to_transaction):
    """Отправляет уведомление о новой транзакции всем пользователям со статусом True"""
    # Берём только тех, у кого статус "True"
    users = Users.select().where(Users.status == "True")

    message_text = (
        f"💰 Новая транзакция!\n\n"
        f"• Сумма: {amount} {symbol}\n"
        f"• От: {from_transaction}\n"
        f"• Время: {time}\n"
        f"• Кошелек: {to_transaction}"
    )

    for user in users:
        try:
            await bot.send_message(chat_id=user.id_user, text=message_text)
            logger.info(f"Уведомление отправлено пользователю {user.id_user} о транзакции {transaction_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user.id_user}: {e}")
