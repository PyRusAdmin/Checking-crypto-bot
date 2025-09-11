# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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


def confirmation_keyboard(user_id: int):
    """Клавиатура для подтверждения регистрации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить", callback_data=f"confirm:{user_id}"
                ),
                InlineKeyboardButton(
                    text="Отклонить", callback_data=f"reject:{user_id}"
                )
            ]
        ]
    )
