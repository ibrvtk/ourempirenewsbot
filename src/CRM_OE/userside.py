from config import (
    LOG_OTHERS,
    ID_CRM_OE, ID_CRM_OE_ADMIN, ID_CRM_OE_NONOFFTOP_THREADS
)
from master.functions import delayMessageDelete

from CRM_OE.database.scheme import readUser

from asyncio import create_task

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command


rt = Router()



@rt.message(F.chat.id == ID_CRM_OE, F.message_thread_id.in_(ID_CRM_OE_NONOFFTOP_THREADS))
async def clearOfftop(message: Message):
    user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"

    if message.text and (message.text.startswith("//") or message.text.startswith("((")):
        create_task(delayMessageDelete(message, 600))
        print(f"(+) @CRM_OE: {message.message_thread_id}: Создан таймер на удаление оффтопа ({user}).") if LOG_OTHERS else None
        

@rt.message(F.chat.id == ID_CRM_OE_ADMIN, Command("who"))
@rt.message(F.chat.id == ID_CRM_OE_ADMIN, F.text.lower() == "ты кто")
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