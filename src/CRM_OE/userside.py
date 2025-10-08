from config import logOther, ID_CRM_OE, ID_CRM_OE_ADMIN, delayMsgDelete
from CRM_OE.database.scheme import readUser

from asyncio import create_task

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command


userside = Router()
NONOFFTOPTOPICS = (43950, 43927, 44448) # Заявления, альянсы, мемы



@userside.message(F.chat.id == ID_CRM_OE, F.message_thread_id.in_(NONOFFTOPTOPICS))
async def clearOfftop(message: Message):
    if message.text and (message.text.startswith("//") or message.text.startswith("((")):
        create_task(delayMsgDelete(message, 600))
        user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"
        print(f"(+) @CRM_OE: {message.message_thread_id}: создан таймер на удаление оффтопа ({user}).") if logOther else None
        

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