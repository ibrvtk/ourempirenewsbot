from config import (
    BOT,
    LOG_ERRORS,
    ID_CRM_OE_ADMIN, ID_CRM_OE_ADMIN_BOT_THREAD,
    PREFIX, SUPERADMIN
)

from CRM_OE.database.scheme import createOrUpdateUser, readUser, deleteUser

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject


rt = Router()

help_user_notice = "Не знаете как пользоваться командой? Пропишите <code>/help user</code>"



@rt.message(F.chat.id == ID_CRM_OE_ADMIN, Command("user"))
async def cmd(message: Message, command: CommandObject):
    if message.message_thread_id != ID_CRM_OE_ADMIN_BOT_THREAD:
        cleared_chat_id = str(message.chat.id).replace("-100", "")
        link = f"https://t.me/c/{cleared_chat_id}/{ID_CRM_OE_ADMIN_BOT_THREAD}"
        await message.reply(f"Эту команду можно использовать только в <a href='{link}'>топике бота</a>.")
        return
    
    if command.args is None:
        await message.reply(f"❌ <b>Ошибка.</b> Отсутствуют аргументы.\n{help_user_notice}.")
        return
    
    args = command.args.split()

    if len(args) == 1:
        await message.reply(f"❌ <b>Ошибка.</b> Слишком мало аргументов.\n{help_user_notice}.")
        return
    
    elif len(args) == 2:
        if args[0] in ("создать", "добавить", "create", "touch"):
            try:
                user_id = int(args[1])
                user = await BOT.get_chat(user_id)
                await createOrUpdateUser(user_id, 0, 0, 0, "None", "🏴", 0, "None", "None", 0)
                user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                await message.reply(f"✅ <b>{user_user} добавлен в БД.</b>")

            except ValueError:
                await message.reply("❌ <b>Ошибка.</b> Некорректный Телеграм ID.")
                return
            except Exception as e:
                await message.reply(f"❌ <b>Ошибка.</b> Возможно у бота нет переписки с этим человеком. "
                                    "Во всяком случае, бот не может установить с ним связь.\n\n"
                                    f"<blockquote><b>Raw вид ошибки:</b>\n{e}</blockquote>")

        if args[0] in ("прочитать", "read", "cat"):
            try:
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
                            countryStatus = "<b>Статус страны:</b> Капитулировал\n"
                    case 1:
                        countryStatus = "<b>Статус страны:</b> Пока жив\n"

                if user_data[6] == 1:
                    turnIsSended = "<b>Статус хода:</b> Отправлен\n" if user_data[9] == 1 else "<b>Статус хода:</b> Не отправлен\n"
                elif user_data[6] == 0:
                    turnIsSended = ""

                cursed_symbols = ("(", ")", ",", "'")
                user_data_for_nano = str(user_data)
                for symbol in cursed_symbols:
                    user_data_for_nano = user_data_for_nano.replace(symbol, "")
                user_data_for_nano = f"/user изменить {user_data_for_nano}"

                try:
                    user = await BOT.get_chat(user_id)
                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    intro = f"🛂 <b>Данные {user_user}</b>"
                    outro = ""
                except:
                    intro = f"🛂 <b>Данные <code>{user_id}</code></b>"
                    outro = "<i>Нет переписки с ботом</i>\n"

                await message.reply(f"{intro}\n\n"
                                    f"<b>Уровень администрации:</b> {user_data[1]}\n"
                                    f"<b>Количество очков:</b> {user_data[2]}\n"
                                    f"<b>Репутация:</b> {user_data[3]}\n"
                                    f"<b>Страна:</b> {countryNameWithFlag}\n"
                                    f"{countryStatus}"
                                    f"{turnIsSended}"
                                    f"\n{outro}"
                                    f"<code>{user_data_for_nano}</code>")

            except ValueError:
                await message.reply("❌ <b>Ошибка.</b> Некорректный Телеграм ID.")
                return
            except Exception as e:
                await message.reply(f"❌ <b>Ошибка.</b> Возможно у бота нет переписки с этим человеком или его просто нет в БД. "
                                    "Во всяком случае, бот не может установить с ним связь.\n\n"
                                    f"<blockquote><b>Raw вид ошибки:</b>\n{e}</blockquote>")
                
        if args[0] in ("удалить", "delete", "rm"):
            try:
                user_id = int(args[1])
                try: await deleteUser(user_id)
                except: pass

                try:
                    user = await BOT.get_chat(user_id)
                    user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                    text = f"🗑️ <b>Данные {user_user} удалены.</b>"
                except:
                    text = f"🗑️ <b>Данные <code>{user_id}</code> удалены.</b>"
                    
                await message.reply(f"{text}")

            except ValueError:
                await message.reply("❌ <b>Ошибка.</b> Некорректный Телеграм ID.")
                return
            except Exception as e:
                await message.reply(f"❌ <b>Ошибка!</b> Причина неясна.\n\n"
                                    f"<blockquote><b>Raw вид ошибки:</b>\n{e}</blockquote>")
                
    elif len(args) == 8:
        if args[0] in ("изменить", "update", "nano"):
            try:
                user_id = int(args[1])
                user_data = await readUser(user_id)
                adminLevel = int(args[2])
                points = int(args[3])
                reputation = int(args[4])
                countryName = f"{str(args[5])}"
                countryFlag = f"{str(args[6])}"
                countryStatus = int(args[7])

                user = await BOT.get_chat(user_id)
                await createOrUpdateUser(user_id, adminLevel, points, reputation, countryName, countryFlag, countryStatus, user_data[7], user_data[8], user_data[9])
                user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
                await message.reply(f"✅ <b>Данные {user_user} изменены.</b>")

            except ValueError:
                await message.reply("❌ <b>Ошибка.</b> Некорректный Телеграм ID.")
                return
            except Exception as e:
                await message.reply(f"❌ <b>Ошибка.</b> Возможно у бота нет переписки с этим человеком. "
                                    "Во всяком случае, бот не может установить с ним связь.\n\n"
                                    f"<blockquote><b>Raw вид ошибки:</b>\n{e}</blockquote>")

    else:
        await message.reply("❌ <b>Ошибка.</b> Слишком много аргументов.")