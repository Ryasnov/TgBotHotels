from database.models import create_tables
from tg_bot.tg_bot import bot

if __name__ == '__main__':
    create_tables()
    bot.polling(none_stop=True, timeout=123)
