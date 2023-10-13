from telebot import types


def all_buttons():
    """Функия, возвращающая разметку клавиатуры со всеми командами"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text='/start'),
        types.KeyboardButton(text='/custom'),
        types.KeyboardButton(text='/low'),
        types.KeyboardButton(text='/high'),
        types.KeyboardButton(text='/history'),
        types.KeyboardButton(text='/help')
    ]
    markup.add(*buttons)
    return markup


def start_button():
    """Функия, возвращающая разметку клавиатуры с командой start"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start = types.KeyboardButton(text='/start')
    markup.add(start)
    return markup


def necessary_buttons():
    """Функия, возвращающая разметку клавиатуры с некоторыми командами"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text='/start'),
        types.KeyboardButton(text='/custom'),
        types.KeyboardButton(text='/help'),
        types.KeyboardButton(text='/history')
    ]
    markup.add(*buttons)
    return markup
