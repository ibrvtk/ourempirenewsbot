from config import (
    bot,
    ID_CRM_OE, ID_CRM_OE_ADMIN, ID_CRM_OE_ADMIN_BOT_THREAD, ID_CRM_OE_COUNTRIES_THREAD, ID_CRM_OE_ONLYPLAYERS_THREADS,
    ID, PREFIX
)
from master.functions import answerRawError
from master.logging import logError, logOther

from crm.database.scheme import createUser, updateUser2, updateUser5, updatePoints, readUser, readUsers, deleteUser

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject


rt = Router()

cmdPlayers_cmdHelp_notice = "Не знаете как пользоваться командой? Пропишите <code>/help user</code>."



# Взаимодействие с БД ЦРМ таблица players.db
@rt.message(F.chat.id == ID_CRM_OE_ADMIN, Command("players"))
async def cmdPlayers(message: Message, command: CommandObject) -> None:
    '''
    CRUD-взаимодействие с людьми в таблице при помощи аргументов.
    Узнать подробнееЮ, как взаимодействовать с командой, можно в master/handlers: cmdHelp(): if message.chat.id == ID_CRM_OE_ADMIN: if args[0] == "user" .
    '''
    if message.message_thread_id != ID_CRM_OE_ADMIN_BOT_THREAD:
        cleared_chat_id = str(message.chat.id).replace("-100", "")
        link = f"https://t.me/c/{cleared_chat_id}/{ID_CRM_OE_ADMIN_BOT_THREAD}"
        await message.reply(f"Эту команду можно использовать только в <a href='{link}'>топике бота</a>.")
        return
    
    if command.args is None:
        await message.reply(f"❌ <b>Ошибка.</b> Отсутствуют аргументы.\n{cmdPlayers_cmdHelp_notice}")
        return
    
    args = command.args.split()
    
    try:
        match len(args):
            case 2:
                if int(args[1]) == ID:
                    await message.reply(f"❌ <b>Ошибка.</b> С ботом нельзя взаимодействовать.")
                    return

                elif args[0] in ("создать", "добавить", "create", "add", "touch"):
                    target_id = int(args[1])
                    target_data = await readUser(target_id)
                    user_data = await readUser(message.from_user.id)
                    
                    target = await bot.get_chat(target_id)

                    if not target_data:
                        await createUser(target_id)
                    else:
                        await message.reply(f"❌ <b>Ошибка.</b> Пользователь уже есть в БД.\n<code>/user прочитать {target_id}</code>")
                        return

                    target_user = f"@{target.username}" if target.username else f"{target.first_name} (<code>{target_id}</code>)"
                    await message.reply(f"✅ <b>{target_user} добавлен в БД.</b>\n<code>/user прочитать {target_id}</code>")

                    await logOther(f"(i) crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} touch {target_id} — Успех.")
                    return
                
                elif args[0] in ("прочитать", "read", "cat"):
                    target_id = int(args[1])
                    target_data = await readUser(target_id)
                    user_data = await readUser(message.from_user.id)

                    if not target_data:
                        await message.reply("❌ <b>Ошибка.</b> Пользователя нет в БД.\n"
                                            f"Добавить можно командой <code>/user добавить {target_id}</code>.")
                        return
                    
                    countryName = str(target_data[3]).replace("_", " ")
                    countryNameWithFlag = f"{target_data[4]} {countryName}" if target_data[3] != "None" else "Это не игрок"
                    countryStatus = ""
                    points = target_data[6]
                    turnIsSended = ""

                    match target_data[5]:
                        case 0:
                            if target_data[3] == "None":
                                countryStatus = ""
                            else:
                                countryStatus = "\n<b>Статус страны:</b> Капитулировал"
                        case 1:
                            countryStatus = "\n<b>Статус страны:</b> Пока жив"

                    if target_data[5] == 1:
                        points = f"\n<b>Влияние:</b> {points}"
                        turnIsSended = "\n<b>Статус хода:</b> Отправлен" if target_data[9] == 1 else "\n<b>Статус хода:</b> Не отправлен"
                    elif target_data[5] == 0:
                        points = ""
                        turnIsSended = ""

                    target = await bot.get_chat(target_id)
                    target_user = f"@{target.username}" if target.username else f"{target.first_name} (<code>{target_id}</code>)"
                    intro = f"🛂 <b>Данные {target_user}</b>"
                    target_data_for_nano = ""

                    match user_data[1]:
                        case 2:
                            target_data_for_nano += f"/user изменить {target_id} {target_data[3]} {target_data[4]} {target_data[5]}"
                        case 5:
                            target_data_for_nano += f"/user изменить {target_id} {target_data[1]} {target_data[2]} {target_data[3]} {target_data[4]} {target_data[5]} {target_data[6]}"

                    await message.reply(f"{intro}\n\n"
                                        f"<b>Уровень администрации:</b> {target_data[1]}\n"
                                        f"<b>Репутация:</b> {target_data[2]}\n"
                                        f"<b>Страна:</b> {countryNameWithFlag}"
                                        f"{countryStatus}"
                                        f"{points}"
                                        f"{turnIsSended}"
                                        f"\n\n<code>{target_data_for_nano}</code>")
                    
                    await logOther(f"(i) crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} cat {target_id} — Успех.")
                    return
                    
                elif args[0] in ("удалить", "delete", "rm"):
                    target_id = int(args[1])
                    target_data = await readUser(target_id)

                    if not target_data:
                        await message.reply("❌ <b>Ошибка.</b> Пользователя нет в БД.")
                        return
                    
                    await deleteUser(target_id)

                    target = await bot.get_chat(target_id)
                    target_user = f"@{target.username}" if target.username else f"{target.first_name} (<code>{target_id}</code>)"

                    text = f"🗑️ <b>Данные {target_user} удалены.</b>"
                    await message.reply(f"{text}")

                    await logOther(f"(i) crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} rm {target_id} — Успех.")
                    return
                
                else:
                    await message.reply(f"❌ <b>Ошибка.</b> Неизвестная команда.\n{cmdPlayers_cmdHelp_notice}")
                    return
            
            case 4 | 5 | 8:
                if args[0] in ("изменить", "update", "nano"):
                    target_id = int(args[1])
                    target_data = await readUser(target_id)
                    user_data = await readUser(message.from_user.id)
                    target = await bot.get_chat(target_id)

                    if user_data[1] == 2 and len(args) == 4:
                        countryName = f"{str(args[2])}"
                        countryFlag = f"{str(args[3])}"
                        countryStatus = int(target_data[5])
                        await updateUser2(target_id, countryName, countryFlag, countryStatus)
                    elif user_data[1] == 5 and len(args) == 8:
                        adminLevel = int(args[2])
                        reputation = int(args[3])
                        countryName = f"{str(args[4])}"
                        countryFlag = f"{str(args[5])}"
                        countryStatus = int(args[6])
                        points = int(args[7])
                        await updateUser5(target_id, adminLevel, reputation, countryName, countryFlag, countryStatus, points)
                    else:
                        await message.reply("❌ <b>Ошибка.</b> У Вас нет прав на выполнение этой команды "
                                            "или введено неверное количество аргументов.")
                        return
                            
                    target_user = f"@{target.username}" if target.username else f"{target.first_name} (<code>{target_id}</code>)"
                    await message.reply(f"✅ <b>Данные {target_user} изменены.</b>\n<code>/user прочитать {target_id}</code>")

                    await logOther(f"(i) crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} nano {target_id} — Успех.")
                    return

            case _:
                await message.reply(f"❌ <b>Ошибка.</b> Некорректное количество аргументов.\n{cmdPlayers_cmdHelp_notice}")
                return
            
    except ValueError as e:
        await message.reply("❌ <b>Ошибка.</b> Неправильно написано одно из цифровых значений.\n"
                            "Первым делом проверьте правильность написания TG-ID.")
    except Exception as e:
        if "database is locked" in str(e):
            e_fastcode = "database is locked"
            await answerRawError(message=message, e=e, e_fastcode=e_fastcode)
            await logError(f"crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} & {target_id} — База данных закрыта.")
        elif "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=message, e=e, e_fastcode=e_fastcode)
            await logError(f"crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} & {target_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=message, e=e)
            await logError(f"crm/admin/handlers.py: cmdPlayers(): {message.from_user.id} & {target_id} — {e}.")


@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "+влияние")
@rt.message(F.chat.id == ID_CRM_OE, F.text.lower() == "-влияние")
async def fcmdEditPoints(message: Message) -> None:
    '''Повысить или понизить влияние.'''
    if not message.reply_to_message:
        await message.delete()
        return
    
    target_id = message.reply_to_message.from_user.id

    if target_id == ID or target_id == message.from_user.id:
        await message.delete()
        return
    
    target_data = await readUser(target_id)
    user_data = await readUser(message.from_user.id)

    if user_data[1] < 2:
        await message.delete()
        return
    
    if not target_data:
        await message.reply("❌ <b>Ошибка.</b> Пользователя нет в БД.")
        return
    
    old_points = target_data[6]

    if message.text == "+влияние":
        new_points = old_points + 1
        await updatePoints(target_id, new_points)
        await message.reply(f"⚜️ <b>Влияние повышено</b> ({old_points} → {new_points})<b>.</b>")
        await logOther(f"(i) crm/admin/handlers.py: editPoints(): {message.from_user.id} +влияние {target_id}")

    elif message.text == "-влияние":
        new_points = old_points - 1
        await updatePoints(target_id, new_points)
        await message.reply(f"⚜️ <b>Влияние понижено</b> ({old_points} → {new_points})<b>.</b>")
        await logOther(f"(i) crm/admin/handlers.py: editPoints(): {message.from_user.id} -влияние {target_id}")


@rt.message(F.chat.id == ID_CRM_OE_ADMIN, F.text == f"{PREFIX}страны список")
async def fcmdMakeCountriesList(message: Message) -> None:
    '''
    Автоматическое составление списка игркоков и выкладывание в соответствующий топик ЦРМ.
    Пока что без вывода стран, у которых нет игроков.
    '''
    message = await message.reply("⏱️ <i>Загрузка.</i>")

    users_data = await readUsers()
    text = ""
    count = 0

    await bot.edit_message_text(chat_id=ID_CRM_OE_ADMIN, message_id=message.message_id, text="⏱️ <i>Загрузка..</i>")

    for user in users_data:
        user_id, countryName, countryFlag, countryStatus, adminLevel = user
        if countryName != "None":
            count += 1
            countryName = str(countryName).replace("_", " ")
            user = await bot.get_chat(user_id)
            user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user_id}</code>)"
            text += f"<i>{count}.</i> {countryFlag} • {countryName} • {user_user}\n" if countryStatus == 1 else f"<i>{count}.</i> {countryFlag} • <s>{countryName} • {user_user}</s>\n"

    await bot.edit_message_text(chat_id=ID_CRM_OE_ADMIN, message_id=message.message_id, text="⏱️ <i>Загрузка...</i>")

    await bot.send_message(
        chat_id=ID_CRM_OE,
        message_thread_id=ID_CRM_OE_COUNTRIES_THREAD,
        text=text
    )

    await message.edit_text("✅ <b>Готово!</b>")
    await logOther(f"(i) crm/admin/handlers.py: countriesList(): {message.from_user.id} составил список стран.")


@rt.message(F.chat.id == ID_CRM_OE, F.message_thread_id.in_(ID_CRM_OE_ONLYPLAYERS_THREADS))
async def clearMessageFromNotPlayer(message: Message) -> None:
    '''Удаление сообщений от не игроков в топиках [И] (для игроков).'''
    try:
        users_data = await readUsers()
        player_ids = [user[0] for user in users_data]
        
        if message.from_user.id not in player_ids:
            await message.delete()
            return
        
        for user_id, countryName, countryFlag, countryStatus, adminLevel in users_data:
            if user_id == message.from_user.id and countryName == "None" and adminLevel == 0:
                await message.delete()
                await logOther(f"(V) crm/admin/handlers.py: clearMessageFromNotPlayer(): Успех — Удалено сообщение от не игрока.")
                break
    
    except Exception as e:
        if "message can't be deleted" in str(e):
            e_fastcode = "message can't be deleted"
            await answerRawError(message, e, e_fastcode, False)
            await logError(f"crm/admin/handlers.py: clearMessageFromNotPlayer(): Сообщение не может быть удалено. У бота достаточно прав?")
        else:
            await answerRawError(message=message, e=e, show_error=False)
            await logError(f"crm/admin/handlers.py: clearMessageFromNotPlayer(): {e}.")