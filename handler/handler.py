from aiogram import F
from aiogram.types import CallbackQuery
from loguru import logger
from peewee import *

from system.system import router

# Подключение к БД
db = SqliteDatabase("people.db")


class Users(Model):
    id_user = IntegerField(unique=True)  # ID пользователя
    user_name = TextField()  # Username пользователя
    last_name = TextField()  # Фамилия пользователя
    first_name = TextField()  # Имя пользователя

    class Meta:
        database = db  # Эта модель использует базу данных "people.db".
        table_name = "users"  # Имя таблицы в базе данных


def write_database(id_user, user_name, last_name, first_name):
    db.connect()
    db.create_tables([Users])

    # Запись данных в таблицу Users
    user = Users(id_user=id_user, user_name=user_name, last_name=last_name, first_name=first_name)
    user.save()  # Сохраняем в базу данных.

    db.close()


# Хендлер нажатия на кнопку "register"
@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    id_user = query.from_user.id  # ID пользователя
    user_name = query.from_user.username  # Username пользователя
    last_name = query.from_user.last_name  # Фамилия пользователя
    first_name = query.from_user.first_name  # Имя пользователя

    logger.debug(
        f"ID пользователя: {id_user}, user_name: {user_name}, last_name: {last_name}, first_name: {first_name}")

    write_database(id_user, user_name, last_name, first_name)
    await query.message.answer("✅ Регистрация пройдена")
    await query.answer()  # Чтобы убрать "часики" в Telegram


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)
