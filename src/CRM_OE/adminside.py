from config import (
    BOT,
    #LOG_ERRORS,
    ID_CRM_OE_ADMIN, ID_CRM_OE_ADMIN_BOT_THREAD,
    ID#, PREFIX, SUPERADMIN
)

from CRM_OE.database.scheme import createOrUpdateUser, readUser, deleteUser

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject


rt = Router()

cmduser_cmdhelp_user_notice = "Не знаете как пользоваться командой? Пропишите <code>/help user</code>."



@rt.message(F.chat.id == ID_CRM_OE_ADMIN, Command("user"))
async def cmdUser(message: Message, command: CommandObject):
    if message.message_thread_id != ID_CRM_OE_ADMIN_BOT_THREAD:
        cleared_chat_id = str(message.chat.id).replace("-100", "")
        link = f"https://t.me/c/{cleared_chat_id}/{ID_CRM_OE_ADMIN_BOT_THREAD}"
        await message.reply(f"Эту команду можно использовать только в <a href='{link}'>топике бота</a>.")
        return
    
    if command.args is None:
        await message.reply(f"❌ <b>Ошибка.</b> Отсутствуют аргументы.\n{cmduser_cmdhelp_user_notice}")
        return
    
    args = command.args.split()
    
    try:
        match len(args):
            case 2:
                if int(args[1]) == ID:
                    await message.reply(f"❌ <b>Ошибка.</b> С ботом нельзя взаимодействовать.")
                    return

                elif args[0] in ("создать", "добавить", "create", "add", "touch"):
                    user_id = int(args[1])
                    user_data = await readUser(user_id)
                    user = await BOT.get_chat(user_id)

                    if not user_data:
                        await createOrUpdateUser(user_id)
                    else:
                        await message.reply(f"❌ <b>Ошибка.</b> Пользователь уже есть в БД.\n<code>/user прочитать {user_id}</code>")
                        return

                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    await message.reply(f"✅ <b>{user_user} добавлен в БД.</b>\n<code>/user прочитать {user_id}</code>")
                    return
                
                elif args[0] in ("прочитать", "read", "cat"):
                    user_id = int(args[1])
                    user_data = await readUser(user_id)

                    if not user_data:
                        await message.reply("❌ <b>Ошибка.</b> Пользователя нет в БД.\n"
                                            f"Добавить можно командой <code>/user добавить {user_id}</code>.")
                        return
                    
                    countryName = str(user_data[4]).replace("_", " ")
                    countryNameWithFlag = f"{user_data[5]} {countryName}" if user_data[4] != "None" else "Это не игрок"

                    match user_data[6]:
                        case 0:
                            if user_data[4] == "None":
                                countryStatus = ""
                            else:
                                countryStatus = "\n<b>Статус страны:</b> Капитулировал"
                        case 1:
                            countryStatus = "\n<b>Статус страны:</b> Пока жив"

                    if user_data[6] == 1:
                        turnIsSended = "\n<b>Статус хода:</b> Отправлен" if user_data[9] == 1 else "\n<b>Статус хода:</b> Не отправлен"
                    elif user_data[6] == 0:
                        turnIsSended = ""

                    user = await BOT.get_chat(user_id)
                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    intro = f"🛂 <b>Данные {user_user}</b>"
                    user_data_for_nano = "/user изменить "

                    match user_data[1]:
                        case 21:
                            user_data_for_nano += f"{user_id} {user_data[4]} {user_data[5]} {user_data[6]}"
                        case 22:
                            user_data_for_nano += f"{user_id} {user_data[4]} {user_data[5]}"
                        case 5:
                            user_data_for_nano += f"{user_id} {user_data[1]} {user_data[2]} {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]}"

                    await message.reply(f"{intro}\n\n"
                                        f"<b>Уровень администрации:</b> {user_data[1]}\n"
                                        f"<b>Количество очков:</b> {user_data[2]}\n"
                                        f"<b>Репутация:</b> {user_data[3]}\n"
                                        f"<b>Страна:</b> {countryNameWithFlag}"
                                        f"{countryStatus}"
                                        f"{turnIsSended}"
                                        f"\n\n<code>{user_data_for_nano}</code>")
                    return
                    
                elif args[0] in ("удалить", "delete", "rm"):
                    user_id = int(args[1])
                    await deleteUser(user_id)
                    user = await BOT.get_chat(user_id)

                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    text = f"🗑️ <b>Данные {user_user} удалены.</b>"
                    await message.reply(f"{text}")
                    return
                
                else:
                    await message.reply(f"❌ <b>Ошибка.</b> Неизвестная команда.\n{cmduser_cmdhelp_user_notice}")
                    return
            
            case 4 | 5 | 8:
                if args[0] in ("изменить", "update", "nano"):
                    user_id = int(args[1])
                    user_data = await readUser(user_id)
                    user = await BOT.get_chat(user_id)

                    if user_data[1] == 21 and len(args) == 5:
                        countryName = f"{str(args[2])}"
                        countryFlag = f"{str(args[3])}"
                        countryStatus = int(args[4])
                        await createOrUpdateUser(user_id, countryName=countryName, countryFlag=countryFlag, countryStatus=countryStatus)
                    elif user_data[1] == 22 and len(args) == 4:
                        countryName = f"{str(args[2])}"
                        countryFlag = f"{str(args[3])}"
                        await createOrUpdateUser(user_id, countryName=countryName, countryFlag=countryFlag)
                    elif user_data[1] == 5 and len(args) == 8:
                        adminLevel = int(args[2])
                        points = int(args[3])
                        reputation = int(args[4])
                        countryName = f"{str(args[5])}"
                        countryFlag = f"{str(args[6])}"
                        countryStatus = int(args[7])
                        await createOrUpdateUser(user_id, adminLevel, points, reputation, countryName, countryFlag, countryStatus)
                    else:
                        await message.reply("❌ <b>Ошибка.</b> У Вас нет прав на выполнение этой команды "
                                            "или неверное количество аргументов.")
                        return
                            
                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    await message.reply(f"✅ <b>Данные {user_user} изменены.</b>\n<code>/user прочитать {user_id}</code>")
                    return

            case _:
                await message.reply(f"❌ <b>Ошибка.</b> Некорректное количество аргументов.\n{cmduser_cmdhelp_user_notice}")
                return
            
    except ValueError as e:
        await message.reply("❌ <b>Ошибка.</b> Неправильно написано одно из цифровых значений.\n"
                            "Первым делом проверьте правильность написания TG-ID.")
        return
    except Exception as e:
        await message.reply("❌ <b>Ошибка!</b> Возможно искомый человек не имеет переписки с ботом или его нет в БД.")
        if str(e) != "":
            await message.answer(f"<blockquote><b>Raw ошибка:</b>\n{e}</blockquote>\n<i>Если пусто — <b>скорее всего</b> ошибка одна из тех, что была упомянута выше.</i>")
        return