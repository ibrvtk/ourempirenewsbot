from config import (
    bot,
    ID_OERCHAT_ADMIN,
    SUPERADMINS, DEVELOPER
)
from master.functions import answerRawError
from master.logging import logError, logOther

from oer.admin.master import (
    appealData, messagesData,
    FSMunban,
    unbanWriteAppealIdInDB
)
from oer.admin.keyboards import unbanKeyboardAcceptedActions_
from oer.database.appeals import readUser, updateUser

from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


rt = Router()



# /unban
@rt.callback_query(F.data.startswith("unbanAppealAccept_"))
async def unbanCbAppealAccept(callback: CallbackQuery, state: FSMContext) -> None:
    '''/unban (unbanUni()): Апелляция принята.'''
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
                                        reply_markup=await unbanKeyboardAcceptedActions_(appeal_id))
        
        await bot.send_message(
            chat_id=appellant_id,
            text="✅ <b>Апелляция была принята!</b> У Вас начался диалог с администратором <i>(через бота. Пишите прямо сюда)</i>."
        )

    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=callback.message, e=e, e_fastcode=e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanCbAppealAccept(): {callback.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=callback.message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanCbAppealAccept(): {callback.from_user.id} & {appellant_id} — {e}.")

    # Дискуссия продолжается в handlers: unbanAppellantMessage(): match appellant_message_count: case _.

@rt.callback_query(F.data.startswith("unbanAppealDecline_"))
async def unbanCbAppealDecline(callback: CallbackQuery, state: FSMContext) -> None:
    '''/unban (unbanUni()): Апелляция отклонена.'''
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
        await bot.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Закрытая апелляция</b> — {appellant_user}\n"
                 f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                 f"Отклонена {admin_user}.",
                reply_markup=None
        )

        await bot.send_message(
            chat_id=appellant_id,
            text="🗑 <b>Вашу апелляцию отклонили.</b>"
        )

    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=callback.message, e=e, e_fastcode=e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanCbAppealDecline(): {callback.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=callback.message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanCbAppealDecline(): {callback.from_user.id} & {appellant_id} — {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)

@rt.callback_query(F.data.startswith("unbanAppealTimeout_"))
async def unbanCbAppealTimeout(callback: CallbackQuery, state: FSMContext) -> None:
    '''/unban (unbanUni()): Выдан таймаут.'''
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

        await bot.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Закрытая апелляция</b> — {appellant_user}\n"
                    f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                    f"{admin_user} выдал таймаут на {time_display}.",
                reply_markup=None
        )

        await bot.send_message(
            chat_id=appellant_id,
            text=f"📵 <b>Вам выдали таймаут на {time_display}.</b>"
        )
        
        await logOther(f"(i) oer/admin/callbacks.py: unbanTimeoutSetTime(): {admin_id} выдал таймаут {appellant_id} ({time_display}).")

    except ValueError as e:
        await message.reply("❌ <b>Ошибка.</b> Неправильно написано одно из цифровых значений.\n"
                            "Первым делом проверьте правильность написания TG-ID.")
    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=message, e=e, e_fastcode=e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanTimeoutSetTime(): {message.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanTimeoutSetTime(): {message.from_user.id} & {appellant_id} — {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)


@rt.callback_query(F.data.startswith("unbanAppealAcceptUnban_"))
async def unbanCbUnbanAccept(callback: CallbackQuery, state: FSMContext) -> None:    
    '''/unban (unbanUni()): В разбане разрешено.'''
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

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMINS:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    try:
        await bot.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Решённая апелляция</b> — {appellant_user}\n"
                 f"{admin_user} выдал разбан",
                reply_markup=None
        )

        await bot.send_message(
            chat_id=appellant_id,
            text="🎉 <b>Вы были разбанены!</b> Добро пожаловать. Снова."
        )
        await bot.send_message(
            chat_id=appellant_id,
            text=f"Если во время попытки зайти в какой-либо чат <a href='https://blog.ourempire.ru/chats'>сетки</a> Вам пишет что Вы забанены — это техническая ошибка. Напишите в ЛС @{DEVELOPER}."
        )

        await logOther(f"(i) oer/admin/callbacks.py: unbanCbUnbanAccept(): {admin_id} разбанил {appellant_id}.")
    
    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=callback.message, e=e, e_fastcode=e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanCbUnbanAccept(): {callback.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=callback.message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanCbUnbanAccept(): {callback.from_user.id} & {appellant_id} — {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)

@rt.callback_query(F.data.startswith("unbanAppealDeclineUnban_"))
async def unbanCbUnbanDecline(callback: CallbackQuery, state: FSMContext) -> None:
    '''/unban (unbanUni()): В разбане отказано.'''
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

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMINS:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    try:
        await bot.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=appealData[appellant_id].toAdmin_message_id,
            text=f"🆘 <b>Решённая апелляция</b> — {appellant_user}\n"
                 f"{admin_user} отказал в разбане",
                reply_markup=None
        )

        await bot.send_message(
            chat_id=appellant_id,
            text="❌ <b>Вам отказали в разбане.</b>"
        )

        await logOther(f"(i) oer/admin/callbacks.py: unbanCbUnbanDecline(): {admin_id} не разбанил {appellant_id}.")
    
    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message=callback.message, e=e, e_fastcode=e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanCbUnbanDecline(): {callback.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=callback.message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanCbUnbanDecline(): {callback.from_user.id} & {appellant_id} — {e}.")

    await unbanWriteAppealIdInDB(appellant_id, state)


@rt.callback_query(F.data.startswith("unbanAppealMsgHistoryPrev_"))
async def unbanCbAppealMessageHistoryPrev(callback: CallbackQuery) -> None:
    '''/unban (unbanUni()): Предыдущее сообщение апеллянта в дискуссии.'''
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

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMINS:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    appealData[appellant_id].appellant_message_count -= 1
    appellant_message_count = appealData[appellant_id].appellant_message_count

    if appellant_message_count <= 0:
        appealData[appellant_id].appellant_message_count += 1
        await callback.answer("❌ Это первое сообщение")
        return
    
    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=appealData[appellant_id].toAdmin_message_id,
        text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
             f"<blockquote>{messagesData[appellant_id][f'message_{appellant_message_count}']}</blockquote>\n"
             f"<i>Сообщение №{appellant_message_count}</i>\n\n"
             f"Принят {admin_user}.",
            reply_markup=await unbanKeyboardAcceptedActions_(appeal_id)
    )

@rt.callback_query(F.data.startswith("unbanAppealMsgHistoryNext_"))
async def unbanCbAppealMessageHistoryNext(callback: CallbackQuery) -> None:
    '''/unban (unbanUni()): Следующее сообщение апеллянта в дискуссии.'''
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

    if callback.from_user.id != admin_id and callback.from_user.id != SUPERADMINS:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    appealData[appellant_id].appellant_message_count += 1
    appellant_message_count = appealData[appellant_id].appellant_message_count

    if f"message_{appellant_message_count}" not in messagesData[appellant_id]:
        appealData[appellant_id].appellant_message_count -= 1
        await callback.answer("❌ Это последнее сообщение")
        return
    
    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=appealData[appellant_id].toAdmin_message_id,
        text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
             f"<blockquote>{messagesData[appellant_id][f'message_{appellant_message_count}']}</blockquote>\n"
             f"<i>Сообщение №{appellant_message_count}</i>\n\n"
             f"Принят {admin_user}.",
            reply_markup=await unbanKeyboardAcceptedActions_(appeal_id)
    )