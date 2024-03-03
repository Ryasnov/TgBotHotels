import peewee as pw

from database.models import History, User


def cleaning() -> None:
    """
    Функция удаляющая самый старый запрос из истории

    :return: None
    """
    ids = list()
    reqs = History.select(History.req_id)
    for req in reqs:
        ids.append(req.req_id)
    min_id = min(ids)
    to_del = History.get(History.req_id == min_id)
    to_del.delete_instance()


def add_new(user: User, hotel: dict) -> None:
    """
    Функция добавляющая результат запроса в историю

    :param user: User
    :param hotel: данные по отелю
    :return: None
    """
    request = History(
        user=user.user_id,
        image=hotel['image'],
        region=user.query,
        hotel_name=hotel['name'],
        address=hotel['address'],
        date_in=user.date_in,
        date_out=user.date_out,
        price=hotel['price']
    )
    try:
        request.save()
    except pw.IntegrityError:
        # исключаем повторение отелей в истории
        to_del = History.get(History.hotel_name == request.hotel_name)
        to_del.delete_instance()
        request.save()
