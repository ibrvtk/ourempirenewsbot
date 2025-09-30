import os
from dotenv import load_dotenv; load_dotenv()

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


TOKEN = os.getenv('TOKEN') # Токен бота.
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


DB_PLAYERS_PATH = os.getenv('DB_PLAYERS_PATH')



ID_OERCHAT = os.getenv('ID_OERCHAT')
ID_CRM_OE = os.getenv('ID_CRM_OE')