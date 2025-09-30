from config import ID_CRM_OE, delayMsgDelete, logging
from CRM_OE.database.scheme import readUser

import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command


handlers = Router()
NONOFFTOPTOPICS = (43950, 43927, 44448) # Заявления, альянсы, мемы



@handlers.message((F.chat.id == ID_CRM_OE) & (F.message_thread_id.in_(NONOFFTOPTOPICS)))
async def clearOfftop(message: Message):
    if message.text and message.text.startswith("//"):
        asyncio.create_task(delayMsgDelete(message, 600))
        print(f"(+) @CRM_OE: {message.message_thread_id}: создан таймер на удаление оффтопа (@{message.from_user.username if message.from_user.username else f'{message.from_user.id} {message.from_user.first_name}'}).") if logging else None
        

@handlers.message(F.chat.id == ID_CRM_OE, Command("who"))
@handlers.message(F.chat.id == ID_CRM_OE, F.text.lower() == "ты кто")
async def uniWho(message: Message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        targetCountry = await readUser(target_id)
        if targetCountry:
            await message.reply(f"<b>{targetCountry[3]}</b>")
        else:
            await message.reply("👻 <b>Это не игрок.</b>")