from telebot.handler_backends import StatesGroup, State


class UserState(StatesGroup):
    """Класс для хранения состояний пользователя"""

    city: State = State()
    date_in: State = State()
    date_out: State = State()
    min_price: State = State()
    max_price: State = State()
    quantity: State = State()
    customized: State = State()
    history: State = State()
    offers: State = State()
