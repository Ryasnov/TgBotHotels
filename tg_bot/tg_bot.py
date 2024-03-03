import datetime
import telebot
import peewee as pw

from telegram_bot_calendar import WYearTelegramCalendar
from typing import List
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from telebot.types import Message, CallbackQuery

from settings import TG_TOKEN
from database.functions import cleaning, add_new
from database.models import User, History
from hotels_API.hotels_API import get_response
from tg_bot.buttons import all_buttons, start_button, necessary_buttons, pagi_buttons
from tg_bot.states import UserState

# объявление бота и хранилища состояний
state_storage = StateMemoryStorage()
token = TG_TOKEN
bot = telebot.TeleBot(token=token, state_storage=state_storage)
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

COMMANDS = ('/start', '/settings', '/low', '/high', '/history', '/help',
            'СТАРТ', "НАСТРОЙКИ", "ДЕШЕВЫЕ", "ДОРОГИЕ", "ИСТОРИЯ", "ПОМОЩЬ")


@bot.message_handler(commands=['start'])
def start_message(message: Message) -> None:
    """
    Стартовая команда. Регистрирует пользователя или удаляет состояние и настройки пользователя

    :param message: Message
    :return: None
    """

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    try:
        User.create(
            user_id=user_id,
            user_name=user_name,
            query=None,
            date_in=None,
            date_out=None,
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
        user.query, user_date_in, user.date_out, user.min_price, user.max_price, user.quantity = [None, None, None,
                                                                                                  None, None, None]
        user.save()
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state='*', commands=['settings'])
def set_city(message: Message) -> None:
    """
    Настройка диапазона поиска. Запрашивает у пользователя название региона

    :param message: Message
    :return: None
    """

    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "Вы не зарегистрированы. Введите команду СТАРТ", reply_markup=start_button())
        return

    bot.send_message(user_id, 'Введите город или регион (например: Усть-Каменогорск)',
                     reply_markup=necessary_buttons())
    bot.set_state(message.from_user.id, UserState.city, message.chat.id)


@bot.message_handler(state=UserState.city)
def set_date(message: Message) -> None:
    """
    Настройка диапазона поиска. Запрашивает у пользователя даты

    :param message: Message
    :return: None
    """

    if message.text in COMMANDS:
        bot.delete_state(message.from_user.id, message.chat.id)
        obey(message)
    else:
        user = User.get(user_id=message.from_user.id)
        user.query = message.text
        user.save()
        bot.send_message(user.user_id, 'Выберите дату заезда')
        calendar, step = WYearTelegramCalendar(locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(message.chat.id,

                         f"Выберите месяц",
                         reply_markup=calendar)
        bot.set_state(message.from_user.id, UserState.date_in, message.chat.id)


@bot.callback_query_handler(state=UserState.date_in, func=WYearTelegramCalendar.func())
def set_date_2(callback: CallbackQuery) -> None:
    """
    Настройка диапазона поиска. Запрашивает у пользователя даты

    :param callback: CallbackQuery
    :return: None
    """

    result, key, step = WYearTelegramCalendar(locale='ru', min_date=datetime.date.today()).process(callback.data)
    if not result and key:
        bot.edit_message_text("Выберите число",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result}",
                              callback.message.chat.id,
                              callback.message.message_id)
        user = User.get(user_id=callback.from_user.id)
        user.date_in = result
        user.save()
        bot.set_state(callback.from_user.id, UserState.date_in, callback.message.chat.id)
        bot.send_message(user.user_id, 'Выберите дату выезда')
        calendar, step = WYearTelegramCalendar(locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(user.user_id, 'Выберите месяц', reply_markup=calendar)
        bot.set_state(callback.from_user.id, UserState.date_out, callback.message.chat.id)


@bot.callback_query_handler(state=UserState.date_out, func=WYearTelegramCalendar.func())
def set_date_3(callback: CallbackQuery) -> None:
    """
    Настройка диапазона поиска. Запрашивает у пользователя даты

    :param callback: CallbackQuery
    :return: None
    """

    user = User.get(user_id=callback.from_user.id)
    min_date = user.date_in + datetime.timedelta(days=1)

    result, key, step = WYearTelegramCalendar(locale='ru', min_date=min_date).process(callback.data)
    if not result and key:
        bot.edit_message_text("Выберите число",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        user = User.get(user_id=callback.from_user.id)

        bot.edit_message_text(f"Дата выезда: {result}",
                              callback.message.chat.id,
                              callback.message.message_id)

        user.date_out = result
        user.save()
        # Настройка диапазона поиска. Запрашивает у пользователя минимальную стоимость
        bot.send_message(callback.from_user.id, "Введите минимальную стоимость в $ (например 20)")
        bot.set_state(callback.from_user.id, UserState.min_price, callback.message.chat.id)


@bot.message_handler(state=UserState.min_price)
def set_max_price(message: Message) -> None:
    """
    Настройка диапазона поиска. Запрашивает у пользователя максимальную стоимость

    :param message: Message
    :return: None
    """

    if message.text in COMMANDS:
        bot.delete_state(message.from_user.id, message.chat.id)
        obey(message)
    else:
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
    """
    Настройка диапазона поиска. Запрашивает у пользователя количество предложений

    :param message: Message
    :return: None
    """

    if message.text in COMMANDS:
        bot.delete_state(message.from_user.id, message.chat.id)
        obey(message)
    else:
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
    """
    Настройка диапазона поиска. Завершение настройки

    :param message: Message
    :return None
    """

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
def show_history(message: Message, user_id=None, count=1, previous_message=None) -> None:
    """
    Команда выдающая последние 10 результатов запросов пользователя

    :param message: Message
    :param user_id: уникальный id пользователя telegram
    :param count: счетчик результатов запросов пользователя
    :param previous_message: Message
    :return None
    """

    if user_id is None:
        user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)

    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите СТАРТ", reply_markup=start_button())
        return

    bot.set_state(user.user_id, UserState.history, message.chat.id)
    reqs: List[History] = user.history.order_by(-History.req_id).limit(10)

    requests = list()
    requests.extend((map(str, reversed(reqs))))
    if not requests:
        bot.reply_to(message, 'История запросов пуста', reply_markup=all_buttons())
        return

    hotels_quantity = len(requests)
    hotel = History.get(History.req_id == requests[count - 1])
    info = f'{hotel.region}\n' \
           f'{hotel.hotel_name}\n' \
           f'{hotel.address}\n' \
           f'Дата заезда: {hotel.date_in}\n' \
           f'Дата выезда: {hotel.date_out}\n' \
           f'Стоимость: {hotel.price}'
    bot.send_photo(user_id, photo=hotel.image, caption=info,
                   reply_markup=pagi_buttons(hotel_count=count, quantity=hotels_quantity))
    try:
        bot.delete_message(message.chat.id, previous_message.id)
    except:
        pass


@bot.callback_query_handler(state=UserState.history, func=lambda callback: True)
def show_history_pagi(callback: CallbackQuery) -> None:
    """
    Функция для пагинации результатов запросов

    :param callback: CallbackQuery
    :return None
    """

    if 'to' in callback.data:
        user = User.get(user_id=callback.from_user.id)
        user_id = user.user_id
        count = int(callback.data.split(' ')[1])
        show_history(callback.message, user_id=user_id, count=count, previous_message=callback.message)


@bot.message_handler(state='*', commands=['help'])
def show_commands(message: Message) -> None:
    """
    Команда выдающая информацию по командам бота

    :param message: Message
    :return: None
    """

    bot.reply_to(message,
                 'Доступные команды:\n'
                 '  НАСТРОЙКА (/settings)  -  Настройка критерий поиска\n'
                 '  ДЕШЕВЫЕ (/low) -  Вывод самых дешевых предложений\n'
                 '  ДОРОГИЕ (/high) -  Вывод самых дорогих предложений\n'
                 '  ИСТОРИЯ  (/history) -  История запросов пользователя\n'
                 '  СТАРТ  (/start) -  Запуск/перезапуск программы\n'
                 '  ПОМОЩЬ  (/help) -  Помощь по командам бота',
                 reply_markup=all_buttons())


def show_hotels(message: Message, user_id=None, check_point=False, count=1, previous_message=None) -> None:
    """
    Функция, выдающая результаты запроса пользователя

    :param message: Message
    :param user_id: уникальный id пользователя telegram
    :param check_point: bool
    :param count: порядковый номер
    :param previous_message: Message
    :return: None
    """
    if user_id is None:
        user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    limit = user.step_quantity

    reqs: List[History] = user.history.order_by(-History.req_id).limit(limit)

    requests = list()
    requests.extend((map(str, reversed(reqs))))

    hotel = History.get(History.req_id == requests[count - 1])
    info = f'{hotel.region}\n' \
           f'{hotel.hotel_name}\n' \
           f'{hotel.address}\n' \
           f'Стоимость: {hotel.price}'
    bot.send_photo(user_id, photo=hotel.image, caption=info,
                   reply_markup=pagi_buttons(hotel_count=count, quantity=limit))
    if check_point:
        try:
            bot.delete_message(message.chat.id, previous_message.id)
        except:
            pass


@bot.callback_query_handler(state=UserState.offers, func=lambda callback: True)
def show_hotels_pagi(callback: CallbackQuery) -> None:
    """
    Функция для пагинации результатов запросов

    :param callback: CallbackQuery
    :return: None
    """

    if 'to' in callback.data:
        user = User.get(user_id=callback.from_user.id)
        user_id = user.user_id
        count = int(callback.data.split(' ')[1])
        show_hotels(callback.message, user_id=user_id, check_point=True, count=count, previous_message=callback.message)


@bot.message_handler(state='*', commands=['low'])
def low_command(message: Message) -> None:
    """
    Команда выдающая самые дешёвые результаты поиска

    :param message: Message
    :return: None
    """

    user = User.get(user_id=message.from_user.id)
    hotels = list()
    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите СТАРТ", reply_markup=start_button())
        return

    if user.min_price is not None and user.max_price is not None and user.quantity is not None:
        bot.reply_to(message, 'Начинаю поиск...')
        try:
            hotels = get_response(command='low', region=user.query, date_in=user.date_in, date_out=user.date_out,
                                  min_price=user.min_price, max_price=user.max_price, quantity=user.quantity)
        except KeyError:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду НАСТРОЙКА",
                             reply_markup=necessary_buttons())
        user.step_quantity = len(hotels)
        user.save()
        if not hotels:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду НАСТРОЙКА",
                             reply_markup=necessary_buttons())

        for hotel in hotels:
            # запись результата в историю
            add_new(user=user, hotel=hotel)
            if History.select().count() > 25:
                # оставляем в БД только 25 последних результатов
                cleaning()
            bot.set_state(user.user_id, UserState.offers, message.chat.id)
        show_hotels(message=message)
    else:
        bot.reply_to(message, 'Не указаны критерии поиска. Напишите НАСТРОЙКА', reply_markup=necessary_buttons())
        return


@bot.message_handler(state='*', commands=['high'])
def high_command(message: Message) -> None:
    """
    Команда выдающая самые дорогие результаты поиска

    :param message: Message
    :return: None
    """

    user = User.get(user_id=message.from_user.id)
    hotels = list()

    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите СТАРТ", reply_markup=start_button())
        return

    if user.min_price is not None and user.max_price is not None and user.quantity is not None:
        bot.reply_to(message, 'Начинаю поиск...')
        try:
            hotels = get_response(command='high', region=user.query, date_in=user.date_in, date_out=user.date_out,
                                  min_price=user.min_price, max_price=user.max_price, quantity=user.quantity)
        except KeyError:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду НАСТРОЙКА",
                             reply_markup=necessary_buttons())
        user.step_quantity = len(hotels)
        user.save()
        if not hotels:
            bot.send_message(message.from_user.id, "К сожалению, нет предлождений, отвечающих Вашему запросу\n"
                                                   "Вы можете изменить его критерии, введя команду НАСТРОЙКА",
                             reply_markup=necessary_buttons())

        for hotel in hotels:
            # запись результата в историю
            add_new(user=user, hotel=hotel)
            if History.select().count() > 25:
                # оставляем в БД только 25 последних результатов
                cleaning()
            bot.set_state(user.user_id, UserState.offers, message.chat.id)
        show_hotels(message=message)
    else:
        bot.reply_to(message, 'Не указаны критерии поиска. Напишите НАСТРОЙКА', reply_markup=necessary_buttons())
        return


@bot.message_handler(content_types=['text'])
def obey(message: Message) -> None:
    """
    Функция обеспечивающая выполнение ботом команд даже в режиме ожидания ввода

    :param message: Message
    :return: None
    """
    if message.text in ("СТАРТ", '/start'):
        start_message(message=message)
    elif message.text in ('НАСТРОЙКА', '/settings'):
        set_city(message=message)
    elif message.text in ('ДЕШЕВЫЕ', '/low'):
        low_command(message=message)
    elif message.text in ('ДОРОГИЕ', '/high'):
        high_command(message=message)
    elif message.text in ('ИСТОРИЯ', '/history'):
        show_history(message=message)
    elif message.text in ('ПОМОЩЬ', '/help'):
        show_commands(message=message)
