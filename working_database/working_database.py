from loguru import logger
from peewee import *

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


class Transactions(Model):
    time = DateTimeField()  # Время транзакции
    amount = IntegerField()  # Сумма транзакции
    symbol = TextField()  # Валюта транзакции
    from_transaction = TextField()  # Откуда транзакция
    to_transaction = TextField()  # Куда транзакция

    class Meta:
        database = db
        table_name = "transactions"


# Создаём таблицу при загрузке модуля
db.connect()
db.create_tables([Users, Transactions], safe=True)
db.close()


def write_transaction(time, amount, symbol, from_transaction, to_transaction):
    Transactions.create(time=time, amount=amount, symbol=symbol, from_transaction=from_transaction,
                        to_transaction=to_transaction)


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
