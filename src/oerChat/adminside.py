from config import (
    BOT,
    LOG_ERRORS,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_BOT_THREAD,
    PREFIX, SUPERADMIN
)

from oerChat.keyboards import unbanKeyboard_, unbanKeyboardAcceptedActions_
from oerChat.databases.appeals import createUser, readUser, updateUser

from asyncio import sleep, create_task
from datetime import datetime
from dataclasses import dataclass

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


rt = Router()

appealData = {}
messagesData = {}



'''/unban'''
# appellant — подающий апелляцию, admin — принимающий.
class FSMunban(StatesGroup):
    text = State() # Сообщение апеллянта. Значение сливается в `messageData[appellant_id][f'message_{messageCount}']`, а после обнуляется.
    time = State() # Установка времени таймаута админом (unbanCbAppealTimeout).

@dataclass
class AppealDataclass: # Данные апелляции.
    appellant_id: int
    appellant_user: str = ""
    admin_id: int = 0
    admin_user: str = ""
    appeal_id: str = ""
    appeal_isAccepted: bool = False # Принята ли апелляция;
    appeal_status: bool = True      # Существует ли апелляция.
    toAdmin_message_id: int = 0
    appellant_message_count: int = 0


async def unbanAppealStatusCheck(appellant_id: int) -> bool: # Проверка статуса апелляции. Если закрыта, то чистит память и FSM.
    global appealData
    global messagesData
    
    if appellant_id not in appealData:
        return False
    
    appeal_status = appealData[appellant_id].appeal_status
    
    if not appeal_status:
        del appealData[appellant_id]
        del messagesData[appellant_id]
        return False
    
    return True

async def unbanWriteAppealIdInDB(appellant_id: int, state: FSMContext) -> None: # Запись ID апелляции в БД.
    global appealData
    appellant_data = await readUser(appellant_id)
    appeal_id = appealData[appellant_id].appeal_id

    if appellant_data[1] == "None":
        appeal_id_for_database = f"{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)
    else:
        appeal_id_for_database = f"{appellant_data[1]}{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)

    appealData[appellant_id].appeal_status = False
    try: await state.clear()
    except: pass
    await unbanAppealStatusCheck(appellant_id)

async def unbanNoMessageTimeout(appellant_id: int, state: FSMContext) -> None: # Если в течение 24 часов апелляция не была решена, то она закрывается.
    global appealData
    global messagesData

    await sleep(86400) # 86к сек. = 24 часа. При изменении - обратить внимание на 108 и 117 строки.

    if appellant_id not in appealData:
        return
    
    if not appealData[appellant_id].appeal_status:
        return

    if appealData[appellant_id].appeal_isAccepted:
        return
    
    appellant_user = appealData[appellant_id].appellant_user

    try:
        if appealData[appellant_id].admin_id != 0:
            await BOT.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Истёкшая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id][f'message_{appealData[appellant_id].appellant_message_count}']}</blockquote>\n\n"
                     f"Принял {appealData[appellant_id].admin_user}\n"
                     f"Прошло 24 часа, но решение так и не было вынесено.",
                    reply_markup=None
            )
        else:
            await BOT.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Истёкшая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                     f"Прошло 24 часа, но жалоба так и не была решена.",
                    reply_markup=None
            )

        await BOT.send_message(
            chat_id=appellant_id,
            text=("⏰ <b>Ваша жалоба была автоматически закрыта.</b> Прошли сутки, а она не продвинулась.")
        )

    except TelegramBadRequest as e:
        print(f"(X) oerChat/adminside.py: unbanNoMessageTimeout(): TelegramBadRequest — {e}.") if LOG_ERRORS else None
    except Exception as e:
        print(f"(XX) oerChat/adminside.py: unbanNoMessageTimeout(): {e}.")

    try: await state.clear()
    except: pass
    await unbanWriteAppealIdInDB(appellant_id, state)


# Непосредственный ввод команды /unban .
@rt.message(F.chat.type == "private", F.text.lower() == f"{PREFIX}апелляция")
@rt.message(F.chat.type == "private", Command("unban"))
async def unbanUni(message: Message, state: FSMContext) -> None:
    global appealData
    global messagesData
    appellant_id = message.from_user.id
    appellant_user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} (<code>{message.from_user.id}</code>)"
    await createUser(appellant_id)
    appellant_data = await readUser(appellant_id)

    if appellant_data[2] > datetime.now().timestamp():
        timeout_end = datetime.fromtimestamp(appellant_data[2])
        await message.reply(f"📵 У вас активен таймаут до <b>{timeout_end.strftime('%d.%m.%Y %H:%M')}</b>.")
        return

    if appellant_id in appealData:
        await message.reply("❌ <b>У вас уже есть открытая апелляция!</b>")
        return
    
    from random import choice, randint
    appeal_codename = choice(["Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "Alpha", "Bravo", "Kilo"])
    appeal_id = f"{appellant_id}_{appeal_codename}_{randint(0, 9)}"

    if appellant_data and appellant_data[1] != "None":
        existing_ids = appellant_data[1].split(", ")
        while appeal_id in existing_ids:
            appeal_codename = choice(["Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "Alpha", "Bravo", "Kilo"])
            appeal_id = f"{appellant_id}_{appeal_codename}_{randint(0, 9)}"

    appealData[appellant_id] = AppealDataclass(
        appellant_id = appellant_id,
        appellant_user = appellant_user,
        appeal_id = appeal_id
    )

    messagesData[appellant_id] = {}

    await state.set_state(FSMunban.text)

    await message.reply(f"🆘 <b>Апелляция на разбан</b> — {appellant_user}\n"
                        "Ваше следующее сообщение будет переслано в чат администрации, откуда с Вами будет производиться общение.\n"
                        "Опишите за что Вас забанили, замутили или выдали пред и почему Вы нарушали правила.\n\n"
                        f"<i>Для отмены напишите /cancel или <code>{PREFIX}отмена</code>.</i>")
    
    await message.answer("<i>Если Вы не забанены, но подаёте апелляцию, то Вы получите глобан и временный запрет на подачу апелляций.</i>")

    await unbanNoMessageTimeout(appellant_id, state)
    
# Апеллянт отправил сообщение.
@rt.message(FSMunban.text)
async def unbanAppellantMessage(message: Message, state: FSMContext) -> None: # Приём сообщений от апеллянта.
    appellant_id = message.from_user.id

    appeal_active = await unbanAppealStatusCheck(appellant_id)
    if not appeal_active:
        return

    if not message.text:
        await message.reply("❌ <b>Ошибка.</b> В данный момент бот не принимает медиафайлы.")
        return
    
    global appealData
    global messagesData
    
    appellant_user = appealData[appellant_id].appellant_user
    appeal_id = appealData[appellant_id].appeal_id

    appealData[appellant_id].appellant_message_count += 1
    appellant_message_count = appealData[appellant_id].appellant_message_count
    message_N = f"message_{appellant_message_count}"

    if appellant_message_count > 1 and not appealData[appellant_id].appeal_isAccepted:
        appealData[appellant_id].appellant_message_count -= 1
        await message.reply("🛂 <b>Вашу апелляцию ещё не приняли.</b>")
        return

    match appellant_message_count:
        # Если это первое сообщение человека (отправка апелляции).
        case 1:
            messagesData[appellant_id][message_N] = message.text

            toAdmin_message = await BOT.send_message(
                chat_id=ID_OERCHAT_ADMIN,
                message_thread_id=ID_OERCHAT_ADMIN_BOT_THREAD,
                text=f"🆘 <b>Новая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{message.text}</blockquote>",
                    reply_markup=unbanKeyboard_(appeal_id)
            )
            appealData[appellant_id].toAdmin_message_id = toAdmin_message.message_id

            await message.reply("✅ <b>Апелляция была отправлена.</b> Ожидайте ответа от модерации.")

        # Если апелляция уже принята и человек ведёт переписку.
        case _:
            messagesData[appellant_id][message_N] = message.text

            await BOT.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id][message_N]}</blockquote>\n"
                     f"<i>Сообщение №{appellant_message_count}</i>\n\n"
                     f"Принят {appealData[appellant_id].admin_user}.",
                    reply_markup=unbanKeyboardAcceptedActions_(appeal_id)
            )

            await BOT.set_message_reaction(
                chat_id=appellant_id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": "👍"}]
            )


# Апелляция принята.
@rt.callback_query(F.data.startswith("unbanAppealAccept_"))
async def unbanCbAppealAccept(callback: CallbackQuery, state: FSMContext) -> None:
    global appealData
    global messagesData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    appealData[appellant_id].admin_id = callback.from_user.id
    appealData[appellant_id].admin_user = admin_user
    appealData[appellant_id].appeal_isAccepted = True

    try:
        await callback.message.edit_text(f"🆘 <b>Апелляция</b> — {appellant_user}\n"
                                         f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                                         f"Принят {admin_user}.",
                                        reply_markup=unbanKeyboardAcceptedActions_(appeal_id))
        
        await BOT.send_message(
            chat_id=appellant_id,
            text="✅ <b>Апелляция была принята!</b> У Вас начался диалог с администратором <i>(через бота. Пишите прямо сюда)</i>."
        )

    except TelegramBadRequest as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Ошибка.</b> Возможно этот человек удалил переписку с ботом. "
                                     "Во всяком случае, бот не может установить с ним связь. Апелляция была закрыта.\n\n"
                                     f"<blockquote><b>Код ошибки:</b>\n{e}</blockquote>")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(X) oerChat/adminside.py: unbanCbAppealAccept(): TelegramBadRequest: {e}.") if LOG_ERRORS else None
        await unbanWriteAppealIdInDB(appellant_id, state)
        return
    except Exception as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Непрдевиденная ошибка</b> при попытке связаться с этим человеком. Для конкретики нужно посмотреть логи. Апелляция была закрыта.")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(XX) oerChat/adminside.py: unbanCbAppealAccept(): {e}.")
        await unbanWriteAppealIdInDB(appellant_id, state)
        return

    # Дискуссия продолжается в `unbanAppellantMessage`: `match appellant_message_count`: `case _`.
    
# Апелляция отклонена.
@rt.callback_query(F.data.startswith("unbanAppealDecline_"))
async def unbanCbAppealDecline(callback: CallbackQuery, state: FSMContext) -> None:
    global appealData
    global messagesData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    appealData[appellant_id].admin_id = callback.from_user.id
    appealData[appellant_id].admin_user = admin_user

    try:
        await BOT.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Закрытая апелляция</b> — {appellant_user}\n"
                 f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                 f"Отклонена {admin_user}.",
                reply_markup=None
        )

        await BOT.send_message(
            chat_id=appellant_id,
            text="🗑 <b>Вашу апелляцию отклонили.</b>"
        )

    except TelegramBadRequest as e:
        print(f"(X) oerChat/adminside.py: unbanCbAppealDecline(): TelegramBadRequest: {e}.") if LOG_ERRORS else None
    except Exception as e:
        print(f"(XX) oerChat/adminside.py: unbanCbAppealDecline(): {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)

# Выдан таймаут.
@rt.callback_query(F.data.startswith("unbanAppealTimeout_"))
async def unbanCbAppealTimeout(callback: CallbackQuery, state: FSMContext) -> None:
    global appealData
    global messagesData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    admin_id = callback.from_user.id
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{admin_id}</code>)"
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    appealData[appellant_id].admin_id = callback.from_user.id
    appealData[appellant_id].admin_user = admin_user

    await state.clear()
    await state.set_state(FSMunban.time)
    await state.update_data(appellant_id=appellant_id)

    await callback.message.edit_text("⏱️ Напишите в <b>следующем</b> сообщении время в <b>секундах,</b> "
                                     "на которое этот человек лишится возможности контактировать с ботом. <b>Просто число.</b>")
    
@rt.message(FSMunban.time)
async def unbanTimeoutSetTime(message: Message, state: FSMContext) -> None:
    global appealData
    global messagesData
    data = await state.get_data()
    appellant_id = data.get('appellant_id')
    appellant_user = appealData[appellant_id].appellant_user
    admin_id = appealData[appellant_id].admin_id
    admin_user = appealData[appellant_id].admin_user

    if not appellant_id or appellant_id not in appealData:
        return

    if message.from_user.id != admin_id:
        return

    try:
        time_seconds = int(message.text.strip())

        if time_seconds <= 0:
            await message.reply("❌ Время должно быть положительным числом!")
            return

        timeout = int(datetime.now().timestamp()) + time_seconds
        
        if time_seconds < 60: time_display = f"{time_seconds} секунд"
        elif time_seconds < 3600: time_minutes = time_seconds // 60; time_display = f"{time_minutes} минут"
        else: time_hours = time_seconds // 3600; time_display = f"{time_hours} часов"
        
        await updateUser(appellant_id, timeout=timeout)

        try:
            await BOT.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Закрытая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                     f"{admin_user} выдал таймаут на {time_display}.",
                    reply_markup=None
            )

            await BOT.send_message(
                chat_id=appellant_id,
                text=f"📵 <b>Вам выдали таймаут на {time_display}.</b>"
            )

        except TelegramBadRequest as e:
            print(f"(X) oerChat/adminside.py: unbanFSMtime(): TelegramBadRequest: {e}.") if LOG_ERRORS else None
            return
        
        await unbanWriteAppealIdInDB(appellant_id, state)

    except ValueError:
        await message.reply("❌ <b>Ошибка!</b> Нужно отправить секунды числом. Попробуйте снова.")
        print(f"(X) oerChat/adminside.py: unbanFSMtime(): ValueError: {e}.") if LOG_ERRORS else None
        return
    except Exception as e:
        await message.reply("❌ <b>Непредвиденная ошибка!</b> Для конкретики нужно посмотреть логи. Попробуйте снова.")
        print(f"(XX) oerChat/adminside.py: unbanFSMtime(): {e}.")
        return


# В разбане разрешено.
@rt.callback_query(F.data.startswith("unbanAppealAcceptUnban_"))
async def unbanCbUnbanAccept(callback: CallbackQuery, state: FSMContext) -> None:    
    global appealData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_id = appealData[appellant_id].admin_id
    admin_user = appealData[appellant_id].admin_user
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    try:
        await BOT.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Решённая апелляция</b> — {appellant_user}\n"
                 f"{admin_user} выдал разбан",
                reply_markup=None
        )

        await BOT.send_message(
            chat_id=appellant_id,
            text="🎉 <b>Вы были разбанены!</b> Добро пожаловать. Снова."
        )
        await BOT.send_message(
            chat_id=appellant_id,
            text="Если во время попытки зайти в какой-либо чат <a href='https://blog.ourempire.ru/chats'>сетки</a> Вам пишет что Вы забанены — это техническая ошибка. Напишите в ЛС @vkuskiy."
        )
    
    except TelegramBadRequest as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Ошибка.</b> Возможно этот человек удалил переписку с ботом. Во всяком случае, бот не может установить с ним связь. Апелляция была закрыта.")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(X) oerChat/adminside.py: unbanCbAppealAcceptUnban(): TelegramBadRequest: {e}.") if LOG_ERRORS else None
    except Exception as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Непрдевиденная ошибка</b> при попытке связаться с этим человеком. Для конкретики нужно посмотреть логи. Апелляция была закрыта.")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(XX) oerChat/adminside.py: unbanCbAppealAcceptUnban(): {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)

# В разбане отказано.
@rt.callback_query(F.data.startswith("unbanAppealDeclineUnban_"))
async def unbanCbUnbanDecline(callback: CallbackQuery, state: FSMContext) -> None:
    global appealData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_id = appealData[appellant_id].admin_id
    admin_user = appealData[appellant_id].admin_user
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    try:
        await BOT.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Решённая апелляция</b> — {appellant_user}\n"
                 f"{admin_user} отказал в разбане",
                reply_markup=None
        )

        await BOT.send_message(
            chat_id=appellant_id,
            text="❌ <b>Вам отказали в разбане.</b>"
        )
    
    except TelegramBadRequest as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Ошибка.</b> Возможно этот человек удалил переписку с ботом. Во всяком случае, бот не может установить с ним связь. Апелляция была закрыта.")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(X) oerChat/adminside.py: unbanCbAppealDeclineUnban(): TelegramBadRequest: {e}.") if LOG_ERRORS else None
    except Exception as e:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.reply("❌ <b>Непрдевиденная ошибка</b> при попытке связаться с этим человеком. Для конкретики нужно посмотреть логи. Апелляция была закрыта.")
        await callback.message.edit_reply_markup(reply_markup=None)
        print(f"(XX) oerChat/adminside.py: unbanCbAppealDeclineUnban(): {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)


# Прошлое сообщение апеллянта в дискуссии.
@rt.callback_query(F.data.startswith("unbanAppealMsgHistoryPrev_"))
async def unbanCbAppealMessageHistoryPrev(callback: CallbackQuery) -> None:
    global appealData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_id = appealData[appellant_id].admin_id
    admin_user = appealData[appellant_id].admin_user
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    appealData[appellant_id].appellant_message_count -= 1
    appellant_message_count = appealData[appellant_id].appellant_message_count

    if appellant_message_count <= 0:
        appealData[appellant_id].appellant_message_count += 1
        await callback.answer("❌ Это первое сообщение")
        return
    
    await BOT.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=appealData[appellant_id].toAdmin_message_id,
        text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
             f"<blockquote>{messagesData[appellant_id][f'message_{appellant_message_count}']}</blockquote>\n"
             f"<i>Сообщение №{appellant_message_count}</i>\n\n"
             f"Принят {admin_user}.",
            reply_markup=unbanKeyboardAcceptedActions_(appeal_id)
    )

# Следующее сообщение апеллянта в дискуссии.
@rt.callback_query(F.data.startswith("unbanAppealMsgHistoryNext_"))
async def unbanCbAppealMessageHistoryNext(callback: CallbackQuery) -> None:
    global appealData
    appellant_id = int(callback.data.split("_")[1])

    if appellant_id not in appealData:
        await callback.answer("❓ Апелляция не найдена")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    appellant_user = appealData[appellant_id].appellant_user
    admin_id = appealData[appellant_id].admin_id
    admin_user = appealData[appellant_id].admin_user
    appeal_id = appealData[appellant_id].appeal_id
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")

    for existing_id in appeal_ids:
        if appeal_id == existing_id:
            await callback.answer("❓ Апелляция не найдена")
            await callback.message.edit_reply_markup(reply_markup=None)
            return

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    appealData[appellant_id].appellant_message_count += 1
    appellant_message_count = appealData[appellant_id].appellant_message_count

    if f"message_{appellant_message_count}" not in messagesData[appellant_id]:
        appealData[appellant_id].appellant_message_count -= 1
        await callback.answer("❌ Это последнее сообщение")
        return
    
    await BOT.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=appealData[appellant_id].toAdmin_message_id,
        text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
             f"<blockquote>{messagesData[appellant_id][f'message_{appellant_message_count}']}</blockquote>\n"
             f"<i>Сообщение №{appellant_message_count}</i>\n\n"
             f"Принят {admin_user}.",
            reply_markup=unbanKeyboardAcceptedActions_(appeal_id)
    )


# Админ отправил сообщение.
@rt.message(F.chat.id == ID_OERCHAT_ADMIN, F.message_thread_id == ID_OERCHAT_ADMIN_BOT_THREAD, F.reply_to_message != None, F.text)
async def unbanAdminMessage(message: Message) -> None:
    global appealData
    appellant_id = None
    replied_id = message.reply_to_message.message_id
    
    for a_id, data in appealData.items():
        if data.admin_id == message.from_user.id and data.appeal_isAccepted and data.toAdmin_message_id == replied_id:
            appellant_id = a_id
            break

    if appellant_id is None:
        return

    try:
        await BOT.send_message(
            chat_id=appellant_id,
            text=(f"🆘 <b>Сообщение от модерации</b>\n"
                  f"<blockquote>{message.text}</blockquote>")
        )

    except Exception as e:
        print(f"(XX) oerChat/adminside.py: unbanAdminMessage(): {e}.") if LOG_ERRORS else None
        return
    

# Люто очистить всю память appealData и messagesData .
@rt.message(F.chat.id == ID_OERCHAT_ADMIN, F.from_user.id == SUPERADMIN, F.text.lower() == f"{PREFIX}очистить апелляции")
async def unbanClearData(message: Message) -> None:
    if message.message_thread_id != ID_OERCHAT_ADMIN_BOT_THREAD:
        await message.reply("Эту команду можно вводить только в топике с <a href='https://t.me/c/2062958469/65368'>жалобами</a>.")
        return

    keyboard = InlineKeyboardBuilder([
        [InlineKeyboardButton(text="✅ Да", callback_data="unbanClearDataConfirm"),
         InlineKeyboardButton(text="❌ Нет", callback_data="unbanClearDataCancel")]
    ])

    await message.reply("❓ Вы уверены?",
                        reply_markup=keyboard)

@rt.callback_query(F.data == "unbanClearDataConfirm")
async def unbanClearDataConfirm(callback: CallbackQuery) -> None:
    if callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Ты не суперадмин")
        return

    global appealData
    global messagesData

    appealData = {}
    messagesData = {}

    await callback.message.edit_text("✅ <b>Вся память об апелляциях очищена.</b>",
                                     reply_markup=None)
    
@rt.callback_query(F.data == "unbanClearDataCancel")
async def unbanClearDataCancel(callback: CallbackQuery) -> None:
    if callback.from_user.id != SUPERADMIN:
        await callback.answer("🖕 Ты не суперадмин")
        return

    await callback.message.delete()