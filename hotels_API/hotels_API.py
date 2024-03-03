import requests
from datetime import datetime
from settings import API_KEY

# адреса запросов
url_location = "https://hotels4.p.rapidapi.com/locations/v3/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/v2/list"

# заголовки запросов
headers = {
    "X-RapidAPI-Key": API_KEY
}


def _get_region_id(region: str) -> int or bool:
    """
    Функия, возвращающая id региона

    :param region: название региона
    :return: id региона или False
    """

    url = url_location
    querystring = {"q": region, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        try:
            region_id = response.json()['sr'][0]['gaiaId']
            return region_id
        except IndexError:
            return False
    return False


def _get_all_hotels_data(command: str, reg_id: int, date_in: datetime.date, date_out: datetime.date, min_price: int,
                         max_price: int, quantity: int) -> dict or bool:
    """
    Функия, возвращающая данные по всем отелям отвечающим критериям запроса

    :param command: команда пользователя
    :param reg_id: id региона
    :param date_in: дата заезда
    :param date_out: дата выезда
    :param min_price: минимальная стоимость
    :param max_price: максимальная стоимость
    :param quantity: количество отелей
    :return: данные по всем отелям или False
    """

    year_in, month_in, day_in = str(date_in).split('-')
    year_out, month_out, day_out = str(date_out).split('-')

    sort = "PRICE_LOW_TO_HIGH"
    if command == 'high':
        sort = "PRICE_HIGH_TO_LOW"

    url = url_properties
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",

        "siteId": 300000001,
        "destination": {"regionId": reg_id},
        "checkInDate": {
            "day": int(day_in),
            "month": int(month_in),
            "year": int(year_in)
        },
        "checkOutDate": {
            "day": int(day_out),
            "month": int(month_out),
            "year": int(year_out)
        },
        "rooms": [
            {
                "adults": 1,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": quantity,
        "sort": sort,
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response = response.json()['data']['propertySearch']['properties']
        return response
    return False


def _get_address(hotel_name: str) -> str:
    """
    Функия, возвращающая адрес отеля

    :param hotel_name: название отеля
    :return: адрес отеля
    """

    url = url_location
    querystring = {"q": hotel_name, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    response = requests.get(url, headers=headers, params=querystring)
    try:
        response = response.json()['sr'][0]['hotelAddress']['street']
    except (KeyError, IndexError):
        response = f'Нет данных'
    return response


def collecting(data: list, quantity: int) -> list:
    """
    Функия, выбирающая необходимую информацию по каждому отелю

    :param data: данные по всем отелям
    :param quantity: количество отелей
    :return: список отелей
    """

    offers_quant = len(data)
    if offers_quant < quantity:
        quantity = offers_quant
    all_hotels_list = list()
    for i in range(quantity):
        all_hotels_list.append({'name': data[i]['name'],
                                'address': _get_address(data[i]['name']),
                                'image': data[i]['propertyImage']['image']['url'],
                                'price': data[i]['price']['options'][0]['formattedDisplayPrice']})
    return all_hotels_list


def get_response(command: str, region: str, date_in: datetime.date, date_out: datetime.date, min_price: int,
                 max_price: int, quantity: int) -> list or bool:
    """
    Функия, возвращающая ответ на запрос пользователя

    :param command: команда пользователя
    :param region: название региона
    :param date_in: дата заезда
    :param date_out: дата выезда
    :param min_price: минимальная стоимость
    :param max_price: максимальная стоимость
    :param quantity: количество отелей
    :return: список отелей или False
    """

    city_id = _get_region_id(region)
    if city_id:
        all_hotels_data = _get_all_hotels_data(command, city_id, date_in, date_out, min_price, max_price, quantity)
        if all_hotels_data:
            all_hotels_list = collecting(all_hotels_data, quantity)
            return all_hotels_list
    return False
