import datetime
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
        query (str): город/регион по которому будет проводиться поиск;
        date_in (datetime.date): дата заезда;
        date_out (datetime.date): дата выезда;
        min_price (int): минимальная стоимость;
        max_price (int): максимальная стоимость;
        quantity (int): количество предложений, которые необходимо вывести.
    """

    user_id: int = pw.IntegerField(primary_key=True, unique=True, null=False)
    user_name: str = pw.CharField()
    query: str = pw.CharField(null=True)
    date_in: datetime.date = pw.DateField(null=True)
    date_out: datetime.date = pw.DateField(null=True)
    min_price: int = pw.IntegerField(null=True)
    max_price: int = pw.IntegerField(null=True)
    quantity: int = pw.IntegerField(null=True)
    step_quantity: int = pw.IntegerField(null=True)

    class Meta:
        db_table = 'users'
        order_by = 'user_id'


class History(BaseModel):
    """
    Класс создания таблицы history для хранения последних 10 результатов запросов пользователя.

    Attributes:
        user (int): уникальный id пользователя из таблицы 'User' для связки таблиц;
        req_id (int): id результата запроса;
        image (str): ссылка на изображение;
        region (str): город/регион;
        hotel_name (str): название отеля;
        address (str): адрес отеля;
        date_in (datetime.date): дата заезда;
        date_out (datetime.date): дата выезда;
        price (str): цена.
    """

    user = pw.ForeignKeyField(User, backref='history')
    req_id = pw.AutoField()
    image = pw.CharField()
    region = pw.CharField()
    hotel_name = pw.CharField(unique=True)
    address = pw.CharField()
    date_in: datetime.date = pw.DateField()
    date_out: datetime.date = pw.DateField()
    price = pw.CharField()

    class Meta:
        db_table = 'history'
        order_by = 'user_id'


def create_tables():
    """Функция создания создания таблиц в БД"""

    if not os.path.exists('tg_bot.db'):
        db.create_tables(BaseModel.__subclasses__())
