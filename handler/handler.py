from aiogram import F
from aiogram.types import CallbackQuery
from loguru import logger
from peewee import *

from system.system import router

# Подключение к БД
db = SqliteDatabase("people.db")


class Users(Model):
    id_user = IntegerField(unique=True)  # ID пользователя
    user_name = TextField(null=True)  # Username пользователя
    last_name = TextField(null=True)  # Фамилия пользователя
    first_name = TextField(null=True)  # Имя пользователя

    class Meta:
        database = db
        table_name = "users"


# Создаём таблицу при загрузке модуля
db.connect()
db.create_tables([Users], safe=True)
db.close()


def write_database(id_user, user_name, last_name, first_name):
    """Сохраняем или обновляем данные пользователя"""
    try:
        with db:
            user, created = Users.get_or_create(
                id_user=id_user,
                defaults={
                    "user_name": user_name,
                    "last_name": last_name,
                    "first_name": first_name
                }
            )
            if not created:  # Если уже был в базе — обновим данные
                user.user_name = user_name
                user.last_name = last_name
                user.first_name = first_name
                user.save()

        logger.info(f"Пользователь {id_user} {'зарегистрирован' if created else 'обновлён'} в базе данных.")
    except Exception as e:
        logger.error(f"Ошибка записи в базу: {e}")


@router.callback_query(F.data == "register")
async def callback_register_handler(query: CallbackQuery) -> None:
    id_user = query.from_user.id
    user_name = query.from_user.username
    last_name = query.from_user.last_name
    first_name = query.from_user.first_name

    logger.debug(
        f"ID: {id_user}, username: {user_name}, last_name: {last_name}, first_name: {first_name}"
    )

    write_database(id_user, user_name, last_name, first_name)

    await query.message.answer("✅ Регистрация пройдена")
    await query.answer()  # Убираем "часики" в Telegram


def register_handler() -> None:
    router.callback_query.register(callback_register_handler)
