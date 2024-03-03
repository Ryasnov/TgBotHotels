from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def all_buttons():
    """Функия, возвращающая разметку клавиатуры со всеми командами

    :return: разметка клавиатуры
    """

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text='СТАРТ'),
        KeyboardButton(text='НАСТРОЙКА'),
        KeyboardButton(text='ДЕШЕВЫЕ'),
        KeyboardButton(text='ДОРОГИЕ'),
        KeyboardButton(text='ИСТОРИЯ'),
        KeyboardButton(text='ПОМОЩЬ')
    ]
    markup.add(*buttons)
    return markup


def start_button() -> ReplyKeyboardMarkup:
    """
    Функия, возвращающая разметку клавиатуры с командой start

    :return: разметка клавиатуры
    """

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    start = KeyboardButton(text='СТАРТ')
    markup.add(start)
    return markup


def necessary_buttons() -> ReplyKeyboardMarkup:
    """
    Функия, возвращающая разметку клавиатуры с некоторыми командами

    :return: разметка клавиатуры
    """

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text='СТАРТ'),
        KeyboardButton(text='НАСТРОЙКА'),
        KeyboardButton(text='ПОМОЩЬ'),
        KeyboardButton(text='ИСТОРИЯ')
    ]
    markup.add(*buttons)
    return markup


def pagi_buttons(hotel_count: int, quantity: int) -> InlineKeyboardMarkup:
    """
    Функция, возвращающая разметку клавиатуры с командами для просмотра истории

    :param hotel_count: порядковый номер отеля
    :param quantity: общее количество отелей
    :return: разметка клавиатуры
    """

    markup = InlineKeyboardMarkup()
    left = hotel_count - 1 if hotel_count != 1 else quantity
    right = hotel_count + 1 if hotel_count != quantity else 1
    buttons = [
        InlineKeyboardButton("назад", callback_data=f'to {left}'),
        InlineKeyboardButton(f"{str(hotel_count)}/{str(quantity)}", callback_data='_'),
        InlineKeyboardButton("вперёд", callback_data=f'to {right}')
        ]
    markup.add(*buttons)
    return markup
