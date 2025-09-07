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
