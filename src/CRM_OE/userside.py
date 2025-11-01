from config import (
    ID,
    LOG_OTHERS,
    ID_CRM_OE, ID_CRM_OE_NONOFFTOP_THREADS#,
    #SUPERADMIN
)
from master.functions import delayMessageDelete

from CRM_OE.database.scheme import readUser, updateReputation

from asyncio import create_task
from datetime import datetime
from dataclasses import dataclass

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject


rt = Router()



@rt.message(F.chat.id == ID_CRM_OE, F.message_thread_id.in_(ID_CRM_OE_NONOFFTOP_THREADS))
async def clearOfftop(message: Message):
    user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"

    if message.text and (message.text.startswith("//") or message.text.startswith("((")):
        create_task(delayMessageDelete(message, 600))
        print(f"(+) @CRM_OE: {message.message_thread_id}: Создан таймер на удаление оффтопа ({user}).") if LOG_OTHERS else None
        

@rt.message(F.chat.id == ID_CRM_OE, Command("who"))
@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "ты кто")
async def uniWho(message: Message, command: CommandObject):
    try:
        if command.args is None:
            if not message.reply_to_message:
                await message.delete()
                return
            
            target_id = message.reply_to_message.from_user.id

            if target_id == ID or target_id == message.from_user.id:
                await message.delete()
                return
            
            target_data = await readUser(target_id)

        elif command.args is not None:
            args = command.args.split()
            target_id = int(args[0])
            
            if target_id == message.from_user.id:
                await message.delete()
                return
            
            target_data = await readUser(target_id)

        if target_data:
            if target_data[4] != "None":
                countryName = str(target_data[4]).replace("_", " ")
                countryStatus = "<i>Капитулировал</i> 💀" if target_data[6] == 0 else ""
                await message.reply(f"Это <b>{target_data[5]} {countryName}</b>.\n{countryStatus}")
            else:
                await message.reply("👻 <b>Это не игрок.</b>")
        else:
            await message.reply("👻 <b>Это не игрок!</b>")
        
    except ValueError:
        await message.reply("❌ <b>Ошибка.</b> Некорректный Телеграм ID.")
        return
    except Exception as e:
        print(f"(XX) CRM_OE/userside.py: uniWho(): {e}.")
        return


'''Система репутации'''
@dataclass
class ReputationDataclass:
    user_id: int
    timeout: float

reputationData = {}

@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "+rep")
@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "+реп")
@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "-rep")
@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "-реп")
async def textReputation(message: Message):
    global reputationData
    user_id = message.from_user.id
    current_time = datetime.now().timestamp()

    for user_id_coodown_check in list(reputationData.keys()):
        if current_time > reputationData[user_id_coodown_check].timeout:
            del reputationData[user_id_coodown_check]

    if not message.reply_to_message:
        await message.delete()
        return
    
    target_id = message.reply_to_message.from_user.id

    if target_id == ID or user_id == target_id:
        await message.delete()
        return
    
    if user_id in reputationData:
        if current_time < reputationData[user_id].timeout:
            time_left = reputationData[user_id].timeout - current_time
            hours_left = int(time_left // 3600)
            minutes_left = int((time_left % 3600) // 60)
            await message.reply(f"⏰ <b>Кулдаун ещё {hours_left}ч {minutes_left}м</b>")
            return

    target_data = await readUser(target_id)

    if not target_data:
        return

    old_rep = target_data[3]

    if message.text == "+rep" or message.text == "+реп":
        new_rep = old_rep + 1
        await updateReputation(target_id, new_rep)
        await message.reply(f"🔺 <b>Репутация повышена</b> ({old_rep} → {new_rep})<b>.</b>")

    elif message.text == "-rep" or message.text == "-реп":
        new_rep = old_rep - 1
        await updateReputation(target_id, new_rep)
        await message.reply(f"🔻 <b>Репутация понижена</b> ({old_rep} → {new_rep})<b>.</b>")

    reputationData[user_id] = ReputationDataclass(
        user_id=user_id,
        timeout=current_time + 86400 # 24 часа.
    )