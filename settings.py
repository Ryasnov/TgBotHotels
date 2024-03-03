import os
from dotenv import load_dotenv

# загрузка данных из виртуального окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# зависимости из виртуального окружения
TG_TOKEN = os.getenv('TG_TOKEN')
API_KEY = os.getenv('API_KEY')

# поддерживаемые команды
DEFAULT_COMMANDS = (
    ('low', 'Вывод самых дешевых предложений'),
    ('high', 'Вывод самых дорогих предложений'),
    ('settings', 'Настройка критерий поиска'),
    ('history', 'Вывод истории запросов пользователя'),
    ('help', 'Помощь по командам бота'),
    ('start', 'Запуск/перезапуск программы'),
)
