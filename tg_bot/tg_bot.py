from typing import List

import peewee as pw
import telebot

from telebot.handler_backends import StatesGroup, State
from telebot.storage import StateMemoryStorage
from telebot import custom_filters
from telebot.types import Message

from settings import TG_TOKEN
from database.database import User, History
from hotels_API.hotels_API import get_response
from tg_bot.buttons import all_buttons, start_button, necessary_buttons

# объявление бота и хранилища состояний
state_storage = StateMemoryStorage()
token = TG_TOKEN
bot = telebot.TeleBot(token=token, state_storage=state_storage)
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())


class UserState(StatesGroup):
    """Класс для хранения состояний пользователя"""

    city: State = State()
    min_price: State = State()
    max_price: State = State()
    quantity: State = State()
    customized: State = State()


@bot.message_handler(commands=['start'])
def start_message(message: Message) -> None:
    """Стартовая команда. Регистрирует пользователя или удаляет состояние и настройки пользователя"""

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    try:
        User.create(
            user_id=user_id,
            user_name=user_name,
            query=None,
            min_price=None,
            max_price=None,
            quantity=None
        )
        bot.reply_to(message, f'Здравствуйте {user_name}, рад познакомиться!\n'
                              f'Я могу помочь вам в поиске отеля. Для этого вам нужно задать критерии поиска и я '
                              f'постараюсь выдать один или несколько вариантов.')
        bot.send_message(message.from_user.id, text='Внизу вы видите кнопки с доступными командами. Можете кликать по '
                                                    'ним или вводить самостоятельно.\n'
                                                    'Команда \help выдаст информацию по командам',
                         reply_markup=all_buttons())
    except pw.IntegrityError:
        bot.reply_to(message, f'Чем могу помочь {user_name}?', reply_markup=all_buttons())
        user = User.get(user_id=message.from_user.id)
        user.query, user.min_price, user.max_price, user.quantity = None, None, None, None
        user.save()
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state='*', commands=['custom'])
def set_city(message: Message) -> None:
    """Настройка диапазона поиска. Запрашивает у пользователя название региона"""

    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "Вы не зарегистрированы. Введите команду /start", reply_markup=start_button())
        return

    bot.send_message(user_id, 'Введите город или регион на английском языке (например: ust-kamenogorsk)',
                     reply_markup=necessary_buttons())
    bot.set_state(message.from_user.id, UserState.city, message.chat.id)


@bot.message_handler(state=UserState.city)
def set_min_price(message: Message) -> None:
    """Настройка диапазона поиска. Запрашивает у пользователя минимальную стоимость"""

    user = User.get(user_id=message.from_user.id)
    user.query = message.text
    user.save()
    bot.send_message(message.from_user.id, "Введите минимальную стоимость в $ (например 20)")
    bot.set_state(message.from_user.id, UserState.min_price, message.chat.id)


@bot.message_handler(state=UserState.min_price)
def set_max_price(message: Message) -> None:
    """Настройка диапазона поиска. Запрашивает у пользователя максимальную стоимость"""

    price_str = message.text
    if not price_str.isdigit() or 0 >= int(price_str):
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость в $ (например: 20)')
        return


    user = User.get(user_id=message.from_user.id)
    user.min_price = int(price_str)
    user.save()
    bot.send_message(message.from_user.id, 'Введите максимальную стоимость в $ (например: 100)')
    bot.set_state(message.from_user.id, UserState.max_price, message.chat.id)


@bot.message_handler(state=UserState.max_price)
def set_quantity(message: Message) -> None:
    """Настройка диапазона поиска. Запрашивает у пользователя количество предложений"""

    price_str = message.text
    if not price_str.isdigit():
        bot.send_message(message.from_user.id, 'Введите максимальную стоимость в $ (например: 100)')
        return
    user = User.get(user_id=message.from_user.id)
    if user.min_price > int(price_str):
        bot.reply_to(message, 'Максимальная стоимость должна быть больше минимальной!')
        bot.send_message(message.from_user.id, 'Введите максимальную стоимость в $ (например: 100)')
        return
    user.max_price = int(price_str)
    user.save()
    bot.send_message(message.from_user.id, 'Введите количество предложений, которое хотите получить (от 1 до 25)')
    bot.set_state(message.from_user.id, UserState.quantity, message.chat.id)


@bot.message_handler(state=UserState.quantity)
def finish_custom(message: Message) -> None:
    """Настройка диапазона поиска. Завершение настройки"""

    quant_str = message.text
    if not quant_str.isdigit():
        bot.send_message(message.from_user.id, 'Введите количество предложений, которое хотите получить (от 1 до 25)')
        return
    if 1 > int(quant_str) > 25:
        bot.reply_to(message, "Увы, я не могу выдать больше 25 предложений за раз")
        bot.send_message(message.from_user.id, 'Введите количество предложений, которое хотите получить (от 1 до 25)')
        return

    user = User.get(user_id=message.from_user.id)
    user.quantity = int(quant_str)
    user.save()
    bot.send_message(message.from_user.id, 'Диапазон поиска настроен', reply_markup=all_buttons())
    bot.set_state(message.from_user.id, UserState.customized, message.chat.id)


@bot.message_handler(state='*', commands=['history'])
def show_history(message: Message) -> None:
    """Команда выдающая последние 10 запросов пользователя"""

    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите /start", reply_markup=start_button())
        return

    reqs: List[History] = user.history.order_by(-History.req_id).limit(10)

    requests = list()
    requests.extend((map(str, reversed(reqs))))

    if not requests:
        bot.reply_to(message, 'История запросов пуста', reply_markup=all_buttons())
        return
    else:
        bot.reply_to(message, 'История запросов: ')
        for request in requests:
            bot.send_message(message.from_user.id, request)
        bot.send_message(message.from_user.id, text='Готово', reply_markup=all_buttons())


@bot.message_handler(state='*', commands=['help'])
def show_commands(message: Message) -> None:
    """Команда выдающая информацию по командам бота"""
    bot.reply_to(message,
                 'Доступные команды:\n'
                 '  /custom  -  Настройка критерий поиска\n'
                 '  /low  -  Вывод самых дешевых предложений\n'
                 '  /high -  Вывод самых дорогих предложений\n'
                 '  /history  -  История запросов пользователя\n'
                 '  /start  -  Запуск/перезапуск программы\n'
                 '  /help  -  Помощь по командам бота',
                 reply_markup=all_buttons())


@bot.message_handler(state='*', commands=['low'])
def low_command(message: Message) -> None:
    """Команда выдающая самые дешёвые результаты поиска"""

    user = User.get(user_id=message.from_user.id)
    if user.min_price is not None and user.max_price is not None and user.quantity is not None:
        # запись запроса в историю
        request = History(
            user=user.user_id,
            command='low',
            query=user.query,
            min_price=user.min_price,
            max_price=user.max_price,
            quantity=user.quantity
        )
        request.save()
        bot.reply_to(message, 'Начинаю поиск...')
        hotels = get_response(command='low', region=user.query, min_price=user.min_price, max_price=user.max_price,
                              quantity=user.quantity)
        if not hotels:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду /custom",
                             reply_markup=necessary_buttons())
        else:
            for hotel in hotels:
                bot.send_message(message.from_user.id, f"{hotel['image']}\n"
                                                       f"Название отеля: {hotel['name']};\n"
                                                       f"Адрес: {hotel['address']};\n"
                                                       f"Стоимость за 1 ночь: от {hotel['price']}")
            bot.send_message(message.from_user.id, 'Готово', reply_markup=all_buttons())
    else:
        bot.reply_to(message, 'Не указаны критерии поиска. Напишите /custom', reply_markup=necessary_buttons())
        return


@bot.message_handler(state='*', commands=['high'])
def low_command(message: Message) -> None:
    """Команда выдающая самые дешёвые результаты поиска"""

    user = User.get(user_id=message.from_user.id)
    if user.min_price is not None and user.max_price is not None and user.quantity is not None:
        # запись запроса в историю
        request = History(
            user=user.user_id,
            command='high',
            query=user.query,
            min_price=user.min_price,
            max_price=user.max_price,
            quantity=user.quantity
        )
        request.save()
        bot.reply_to(message, 'Начинаю поиск...')
        hotels = get_response(command='high', region=user.query, min_price=user.min_price, max_price=user.max_price,
                              quantity=user.quantity)
        if not hotels:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду /custom",
                             reply_markup=necessary_buttons())

        else:
            for hotel in hotels:
                bot.send_message(message.from_user.id, f"{hotel['image']}\n"
                                                       f"Название отеля: {hotel['name']};\n"
                                                       f"Адрес: {hotel['address']};\n"
                                                       f"Стоимость за 1 ночь: от {hotel['price']}")
            bot.send_message(message.from_user.id, 'Готово', reply_markup=all_buttons())
    else:
        bot.reply_to(message, 'Не указаны критерии поиска. Напишите /custom', reply_markup=necessary_buttons())
        return
