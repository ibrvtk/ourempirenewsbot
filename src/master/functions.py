from config import (
    bot,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_TERMINAL_THREAD,
    ID_CRM_OE_ADMIN
)
from master.logging import logError, logOther

from asyncio import sleep

from aiogram.types import Message
# from aiogram.exceptions import TelegramBadRequest



async def getUser(user_id: int, return_full: bool = True):
    '''
    Принимаем TG-ID, возвращаем информацию.
    Если return_full = False, то вернёт только переменную user_user.
    '''
    try:
        user = await bot.get_chat(user_id)
    except:
        user_id = f"<code>{user_id}</code>" if not return_full else None
        return user_id

    if return_full:
        return user
    else:
        user_user = f"@{user.username}" if user.username else f"{user.first_name} (<code>{user.id}</code>)"
        return user_user


async def answerRawError(message: Message, e: Exception, e_fastcode: str = "", tgTerminal: bool = False) -> None:
    '''
    Универсальный обработчик ошибок.
    e_factcode — краткое содержание ошибки, по которому её можно быстро идентефицировать.
    tgTerminal — не выводить ошибку пользователю? Обычно использую если ошибка может вывестись, хотя вызывалась не команда (например в crm/admin/handlers.py: clearMessageFromNotPlayer()).
    '''
    error = str(e)
    
    if not tgTerminal:
        if "message can't be deleted" in error:
            await message.reply(f"❌ <b>Ошибка.</b> Сообщение не может быть удалено. У бота достаточно прав?")
        elif "database is locked" in error:
            await message.reply(f"❌ <b>Ошибка.</b> База данных закрыта.")
        elif "chat not found" in error:
            await message.reply(f"❌ <b>Ошибка.</b> Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        elif "message to delete not found" in error:
            await message.reply(f"❌ <b>Ошибка.</b> Сообщение не может быть удалено. Оно уже удалено?")
        else:
            await message.reply(f"❌ <b>Непредвиденная ошибка!</b>\n<blockquote>{error}</blockquote>")

    user_user = await getUser(message.from_user.id, False)
    e_fastcode = "<b>Непредвиденная!</b>\n" if e_fastcode == "" else f"<b>«{e_fastcode}»</b>\n"

    message_chat_id = message.chat.id
    chat_name = ""
    if message_chat_id == ID_CRM_OE_ADMIN:
        chat_name = "Админский чат ЦРМ"
    elif message_chat_id == ID_OERCHAT_ADMIN:
        chat_name = "Админский чат OE"
    elif message.chat.type == "private":
        chat_name = f"Какой-то закрытый чат. TG-ID: <code>{message.chat.id}</code>"
    else:
        chat_name = f"@{message.chat.username}" if message.chat.username else f"<code>{message.chat.id}</code>"

    await bot.send_message(
        chat_id=ID_OERCHAT_ADMIN,
        message_thread_id=ID_OERCHAT_ADMIN_TERMINAL_THREAD,
        text=f"❌ <b>Ошибка</b>\n"
                f"<b>В чате:</b> @{chat_name}\n"
                f"<b>От:</b> {user_user}\n"
                f"<b>Триггер:</b> <code>{message.text}</code>\n"
                f"<blockquote>{e_fastcode}{error}</blockquote>"
    )


async def delayMessageDelete(message: Message, delay: int, isOfftop: bool = False) -> None: # Отложенное удаление сообщения.
    '''
    Отложенное удаление сообщения.
    message — сообщение, которое нужно удалить.
    delay — задержка, с которой нужно удалить message.
    isOfftop — является ли message оффтопом (нужно лишь для уточнения в терминале).
    '''
    await sleep(delay)

    user_id = message.from_user.id
    chat_user = f"@{message.chat.username}" if message.chat.username else message.chat.id
    thread = f"/{message.message_thread_id}" if message.message_thread_id else ""
    placeholderText = f"{thread}: "
    if delay < 60:
        time_display = f"{delay} секунд"
    else:
        delay_minutes = delay // 60
        time_display = f"{delay_minutes} минут"

    try:
        await message.delete()

        if not isOfftop:
            placeholderText += "Удалено сообщение по отложке"
        else:
            placeholderText += "Удалён оффтоп"
            
        logOther(f"(V) master/functions: {chat_user}: {placeholderText} от {user_id} (прошло {time_display}).")

    except Exception as e:
        if "message can't be deleted" in str(e):
            e_fastcode = "message can't be deleted"
            await answerRawError(message=message, e=e, e_fastcode=e_fastcode)
            await logError(f"master/functuons.py: delayMessageDelete(): {chat_user}{thread}: От {user_id} — Сообщение не может быть удалено. У бота достаточно прав?")
        elif "message to delete not found" in str(e):
            e_fastcode = "message to delete not found"
            await answerRawError(message=message, e=e, e_fastcode=e_fastcode)
            await logError(f"master/functuons.py: delayMessageDelete(): {chat_user}{thread}: От {user_id} — Сообщение не может быть удалено. Оно уже удалено?")
        else:
            await answerRawError(message=message, e=e)
            await logError(f"master/functuons.py: delayMessageDelete(): {chat_user}{thread}: От {user_id} — {e}.")