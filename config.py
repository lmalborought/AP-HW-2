import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")

API_KEY_sport = os.getenv('API_KEY_sport')

if not API_KEY_sport:
    raise ValueError("Переменная окружения API_KEY_sport не установлена!")

API_KEY_food = os.getenv('API_KEY_food')

if not API_KEY_food:
    raise ValueError("Переменная окружения API_KEY_food не установлена!")

API_KEY_wether = os.getenv('API_KEY_wether')

if not API_KEY_wether:
    raise ValueError("Переменная окружения API_KEY_wether не установлена!")