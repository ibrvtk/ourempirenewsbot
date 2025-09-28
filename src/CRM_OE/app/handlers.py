from config import CRM_OE

import asyncio

from aiogram import F, Router
from aiogram.types import Message


handlers = Router()
NONOFFTOPTOPICS = (43950, 43927, 44448) # Заявления, альянсы, мемы



async def delayDelete(message: Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()
    print("CRM_OE: заявления: удалён оффтоп (10 минут прошло).")

@handlers.message((F.chat.id == CRM_OE) & (F.message_thread_id.in_(NONOFFTOPTOPICS)))
async def clearOfftop(message: Message):
    if message.text and message.text.startswith("//"):
        asyncio.create_task(delayDelete(message, 600))
        print(f"CRM_OE: {message.message_thread_id}: создан таймер на удаление оффтопа (@{message.from_user.username if message.from_user.username else f'{message.from_user.id} {message.from_user.first_name}'}).")