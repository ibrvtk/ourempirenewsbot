import os
import asyncio
from dotenv import load_dotenv; load_dotenv()

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message


TOKEN = os.getenv('TOKEN') # Токен бота.
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

logging = True



async def delayMsgDelete(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
        placeholderText = f"{message.message_thread_id}: удалён оффтоп " if message.chat.id == ID_CRM_OE else "удалено сообщение по отложке "
        delayInMinutes = delay / 60
        print(f"(V) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText} (прошло {delayInMinutes} минут).")
    except Exception as e:
        placeholderText = f"{message.message_thread_id}: оффтоп не был удалён: " if message.chat.id == ID_CRM_OE else "отложенное удаление сообщение не произошло: "
        print(f"(V) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText} {e}")



DB_PLAYERS_PATH = os.getenv('DB_PLAYERS_PATH')


ID_OERCHAT = int(os.getenv('ID_OERCHAT'))
ID_OERCHAT_ADMIN = int(os.getenv('ID_OERCHAT_ADMIN'))

ID_CRM_OE = int(os.getenv('ID_CRM_OE'))
ID_CRM_OE_ADMIN = int(os.getenv('ID_CRM_OE_ADMIN'))