from config import (
    bot,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_BOT_THREAD,
    PREFIX, SUPERADMINS
)
from master.functions import answerRawError
from master.logging import logError

from oer.admin.master import (
    appealData, messagesData,
    unbanWriteAppealIdInDB
)

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


rt = Router()



# /unban
@rt.message(F.chat.id == ID_OERCHAT_ADMIN, F.message_thread_id == ID_OERCHAT_ADMIN_BOT_THREAD, F.reply_to_message != None, F.text)
async def unbanAdminMessage(message: Message, state: FSMContext) -> None:
    '''/unban (unbanUni()): Админ отправил сообщение.'''
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
            await logError(f"oer/admin/callbacks.py: unbanAdminMessage(): {message.from_user.id} & {appellant_id} — Чат не найден. Искомый человек существует? У него есть переписка с ботом?")
        else:
            await answerRawError(message=message, e=e)
            await logError(f"oer/admin/callbacks`.py: unbanAdminMessage(): {message.from_user.id} & {appellant_id} — {e}.")
        await unbanWriteAppealIdInDB(appellant_id, state)


@rt.message(F.chat.id == ID_OERCHAT_ADMIN, F.from_user.id.in_(SUPERADMINS), F.text.lower() == f"{PREFIX}очистить апелляции")
async def unbanClearData(message: Message) -> None:
    '''/unban (unbanUni()): люто очистить всю память appealData и messagesData .'''
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
    if callback.from_user.id != SUPERADMINS:
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
    if callback.from_user.id != SUPERADMINS:
        await callback.answer("🖕 Ты не суперадмин")
        return

    await callback.message.delete()