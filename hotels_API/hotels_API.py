import requests
from datetime import datetime

from settings import API_KEY, API_HOST

# адреса запросов
url_location = "https://hotels4.p.rapidapi.com/locations/v3/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/v2/list"

# заголовки запросов
headers = {
    "X-RapidAPI-Key": API_KEY,
    'X-RapidAPI-Host': API_HOST
}


def _get_region_id(region: str) -> int or bool:
    """
    Функия, возвращающая id региона.

    Attributes:
        region (str): название региона.
    """

    url = url_location
    querystring = {"q": region, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        try:
            region_id = response.json()['sr'][0]['gaiaId']
            return region_id
        except IndexError:
            return False
    return False


def _get_all_hotels_data(command: str, reg_id: int, min_price: int, max_price: int, quantity: int) -> dict or bool:
    """
    Функия, возвращающая данные по всем отелям отвечающим критериям запроса.

    Attributes:
        command (str): команда пользователя;
        reg_id (int): id региона;
        min_price (int): минимальная стоимость;
        max_price (int): максимальная стоимость;
        quantity(int): количество отелей.
    """

    year = int(datetime.now().strftime("%Y")) + 1
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
            "day": 15,
            "month": 1,
            "year": year
        },
        "checkOutDate": {
            "day": 16,
            "month": 1,
            "year": year
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
    Функия, возвращающая адрес отеля.

    Attributes:
        hotel_name (str): название отеля.
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
    Функия, выбирающая необходимую информацию по каждому отелю.

    Attributes:
        data (list): данные по всем отелям;
        quantity (int): количество отелей.
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


def get_response(command: str, region: str, min_price: int, max_price: int, quantity: int) -> list or bool:
    """
    Функия, возвращающая ответ на запрос пользователя.

    Attributes:
        command (str): команда пользователя;
        region (str): название региона;
        min_price (int): минимальная стоимость;
        max_price (int): максимальная стоимость;
        quantity(int): количество отелей.
    """

    city_id = _get_region_id(region)
    if city_id:
        all_hotels_data = _get_all_hotels_data(command, city_id, min_price, max_price, quantity)
        if all_hotels_data:
            all_hotels_list = collecting(all_hotels_data, quantity)
            return all_hotels_list
    return False
