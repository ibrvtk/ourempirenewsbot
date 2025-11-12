from config import (
    bot,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_BOT_THREAD,
    PREFIX, SUPERADMIN
)
from master.functions import answerRawError
from master.logging import logError, logOther

from oer.admin.master import (
    appealData, messagesData,
    FSMunban, AppealDataclass,
    unbanAppealStatusCheck, unbanNoMessageTimeout, unbanWriteAppealIdInDB
)
from oer.admin.keyboards import unbanKeyboard_, unbanKeyboardAcceptedActions_
from oer.database.appeals import createUser, readUser

from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


rt = Router()



'''/unban'''
# appellant — подающий апелляцию, admin — принимающий.
@rt.message(F.chat.type == "private", Command("unban"))
@rt.message(F.chat.type == "private", F.text.lower() == f"{PREFIX}апелляция")
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

    await logOther(f"(i) oer/admin/handlers.py: unbanUni(): {appellant_id} подал апелляцию.")
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

            toAdmin_message = await bot.send_message(
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

            await bot.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id][message_N]}</blockquote>\n"
                     f"<i>Сообщение №{appellant_message_count}</i>\n\n"
                     f"Принят {appealData[appellant_id].admin_user}.",
                    reply_markup=unbanKeyboardAcceptedActions_(appeal_id)
            )

            await bot.set_message_reaction(
                chat_id=appellant_id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": "👍"}]
            )

# Админ отправил сообщение.
@rt.message(F.chat.id == ID_OERCHAT_ADMIN, F.message_thread_id == ID_OERCHAT_ADMIN_BOT_THREAD, F.reply_to_message != None, F.text)
async def unbanAdminMessage(message: Message, state: FSMContext) -> None:
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
        await bot.send_message(
            chat_id=appellant_id,
            text=(f"🆘 <b>Сообщение от модерации</b>\n"
                  f"<blockquote>{message.text}</blockquote>")
        )

    except Exception as e:
        if "chat not found" in str(e):
            e_fastcode = "chat not found"
            await answerRawError(message, e, e_fastcode)
            await logError(f"oer/admin/callbacks.py: unbanCbAppealDecline(): {message.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanCbAppealDecline(): {message.from_user.id} & {appellant_id} — {e}.")
        await unbanWriteAppealIdInDB(appellant_id, state)


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