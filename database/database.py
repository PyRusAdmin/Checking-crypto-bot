from loguru import logger
from peewee import *

# Подключение к БД
db = SqliteDatabase("database/people.db")


class Users(Model):
    id_user = IntegerField(unique=True)  # ID пользователя
    user_name = TextField(null=True)  # Username пользователя
    last_name = TextField(null=True)  # Фамилия пользователя
    first_name = TextField(null=True)  # Имя пользователя

    class Meta:
        database = db
        table_name = "users"


class Transactions(Model):
    transaction_id = TextField(primary_key=True)  # Уникальный ID транзакции
    time = DateTimeField()  # Время транзакции
    amount = FloatField()  # Сумма транзакции
    symbol = TextField()  # Валюта
    from_transaction = TextField()  # Откуда
    to_transaction = TextField()  # Куда

    class Meta:
        database = db
        table_name = "transactions"


# Создаём таблицу при загрузке модуля
db.connect()
db.create_tables([Users, Transactions], safe=True)
db.close()


async def read_from_db():
    """Функция для чтения данных из базы данных. Считываем данные из базы данных"""
    with db:
        rows = Transactions.select()  # Получаем все записи из таблицы employees
    return rows


def write_database(id_user, user_name, last_name, first_name):
    """Сохраняем или обновляем данные пользователя"""
    try:
        with db:
            user, created = Users.get_or_create(
                id_user=id_user,
                defaults={
                    "user_name": user_name,
                    "last_name": last_name,
                    "first_name": first_name,
                },
            )
            if not created:  # Если уже был в базе — обновим данные
                user.user_name = user_name
                user.last_name = last_name
                user.first_name = first_name
                user.save()

        logger.info(
            f"Пользователь {id_user} {'зарегистрирован' if created else 'обновлён'} в базе данных."
        )
    except Exception as e:
        logger.error(f"Ошибка записи в базу: {e}")


def transaction_exists(tx_id: str) -> bool:
    """Проверяет, существует ли транзакция с таким ID в БД"""
    try:
        return Transactions.select().where(Transactions.transaction_id == tx_id).exists()
    except Exception as e:
        logger.error(f"Ошибка при проверке транзакции {tx_id}: {e}")
        return False
