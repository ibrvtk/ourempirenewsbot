import os
from dotenv import load_dotenv

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


load_dotenv()



TOKEN = os.getenv('TOKEN') # Токен бота.
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


CRM_OE = -1002422414477