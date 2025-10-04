from config import ID_CRM_OE, ID_CRM_OE_ADMIN, delayMsgDelete, loggingOther
from CRM_OE.database.scheme import readUser

import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command


userside = Router()
NONOFFTOPTOPICS = (43950, 43927, 44448) # Заявления, альянсы, мемы



@userside.message(F.chat.id == ID_CRM_OE, F.message_thread_id.in_(NONOFFTOPTOPICS))
async def clearOfftop(message: Message):
    if message.text and (message.text.startswith("//") or message.text.startswith("((")):
        asyncio.create_task(delayMsgDelete(message, 600))
        print(f"(+) @CRM_OE: {message.message_thread_id}: создан таймер на удаление оффтопа (@{message.from_user.username if message.from_user.username else f'{message.from_user.id} {message.from_user.first_name}'}).") if loggingOther else None
        

@userside.message(F.chat.id == ID_CRM_OE_ADMIN, Command("who"))
@userside.message(F.chat.id == ID_CRM_OE_ADMIN, F.text.lower() == "ты кто")
async def uniWho(message: Message):
    if not message.reply_to_message:
        await message.delete()
        return
    
    target_id = message.reply_to_message.from_user.id
    targetCountry = await readUser(target_id)
    if targetCountry  and targetCountry[3] != "None":
        await message.reply(f"Это <b>{targetCountry[3]}</b>.")
    else:
        await message.reply("👻 <b>Это не игрок.</b>")