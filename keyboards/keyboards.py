from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.filters import inline_keyboard


def register_keyboard():
    """Клавиатура для регистрации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация",
                                  callback_data="registration")],
        ]
    )


def main_keyboard():
    """Клавиатура для главного меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Транзакции", callback_data="transactions"),
            ],
            [
                InlineKeyboardButton(
                    text="Транзакции сегодня", callback_data="today_transactions"),
            ]
        ]
    )


def back():
    """Клавиатура для возврата"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад", callback_data="back")

            ]
        ]
    )

def confirmation_keyboard():
    """Клавиатура для подтверждения регистрации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить", callback_data="confirm"
                ),
                InlineKeyboardButton(
                    text="Отклонить", callback_data="reject"
                )
            ]
        ]
    )