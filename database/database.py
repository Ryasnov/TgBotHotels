import os

import peewee as pw


# создание БД
db = pw.SqliteDatabase('tg_bot.db')


class BaseModel(pw.Model):
    """Базовый класс для БД"""

    class Meta:
        database = db


class User(BaseModel):
    """
    Класс создания таблицы User для хранения пользовательских данных.

    Attributes:
        user_id (int): уникальный id пользователя для связки таблиц;
        user_name (str): имя пользователя в tg;
        query (str): услуга/товар, по которым будет проводиться поиск;
        min_price( int): минимальная стоимость;
        max_price (int): максимальная стоимость;
        quantity (int): количество единиц категории (товаров/услуг), которые необходимо вывести.
    """

    user_id: int = pw.IntegerField(primary_key=True, unique=True, null=False)
    user_name: str = pw.CharField()
    query: str = pw.CharField(null=True)
    min_price: int = pw.IntegerField(null=True)
    max_price: int = pw.IntegerField(null=True)
    quantity: int = pw.IntegerField(null=True)

    class Meta:
        db_table = 'users'
        order_by = 'user_id'


class History(BaseModel):
    """
    Класс создания таблицы history для хранения последних 10 запросов пользователя.

    Attributes:
        user (int): уникальный id пользователя из таблицы 'User' для связки таблиц;
        req_id (int): id запроса;
        command (str): команда пользователя;
        query (str): информация, запрашиваемая пользователем;
        min_price( int): минимальная стоимость;
        max_price (int): максимальная стоимость;
        quantity (int): количество единиц категории (товаров/услуг), которые необходимо вывести.
    """

    user = pw.ForeignKeyField(User, backref='history')
    req_id = pw.AutoField()
    command = pw.CharField()
    query = pw.CharField()
    min_price: int = pw.IntegerField()
    max_price: int = pw.IntegerField()
    quantity: int = pw.IntegerField()

    def __str__(self):
        return (f'{self.req_id}.\n'
                f'{self.query}\n'
                f'стоимость от {self.min_price} до {self.max_price}\n'
                f'{self.quantity} предложений\n'
                f'команда {self.command}\n')

    class Meta:
        db_table = 'history'
        order_by = 'user_id'


def create_tables():
    """Функция создания создания таблиц в БД"""

    if not os.path.exists('tg_bot.db'):
        db.create_tables(BaseModel.__subclasses__())
