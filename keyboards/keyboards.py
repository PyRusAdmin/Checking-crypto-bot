from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_keyboard():
    """Клавиатура для регистрации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="registration")],
        ]
    )


if __name__ == '__main__':
    register_keyboard()