from config import bot, logErrors, ID_OERCHAT_ADMIN
import oerChat.app.keyboards as kb

# from oerChat.databases.appeals import updateUser

from dataclasses import dataclass

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


adminside = Router()

conversationData = {}
activeAppeals = {}



# /unban
@dataclass
class fsmUnbanSendAppeal(StatesGroup):
    text = State() # Истории переписки. Значение сливается в conversationData[*][f'msg{msgCount}'], а после обнуляется.

@adminside.message(F.chat.type == "private", Command("unban"))
async def cmdUnban(message: Message, state: FSMContext):
    appellant_id = message.from_user.id
    appelant_user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} (<code>{message.from_user.id}</code>)"

    conversationData[appellant_id] = { # История переписки. msg1 - первое сообщение.
        'appellant_id': appellant_id,
        'appellant_user': appelant_user,
        'admin_id': None,
        'msg1': None
    }

    await state.update_data(msgCount=0)
    await state.set_state(fsmUnbanSendAppeal.text)

    await message.answer(f"🆘 <b>Апелляция на разбан</b> — {appelant_user}\n"
                         "Ваше следующее сообщение будет переслано в чат администрации, откуда с Вами будет производиться общение.\n"
                         "Опишите за что Вас забанили <i>(если знаете или помните)</i> и почему Вы нарушали.\n\n"
                         "<i>На данный момент бот не поддерживает отправку скриншотов.\nДля отмены пропишите /cancel.</i>")
    
@adminside.message(fsmUnbanSendAppeal.text)
async def fsmUnbanSendAppealText(message: Message, state: FSMContext):
    appellant_id = message.from_user.id
    appellant_user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} (<code>{appellant_id}</code>)"

    data = await state.get_data()
    msgCount = data['msgCount'] + 1
    await state.update_data(msgCount=msgCount)
    await state.update_data(text=message.text)

    global conversationData
    conversationData[appellant_id]['msg1'] = message.text

    if message.text:
        await message.reply("✅ <b>Апелляция была отправлена.</b> Ожидайте ответа от модерации.")

        await bot.send_message(
            chat_id=ID_OERCHAT_ADMIN,
            text=f"🆘 <b>Новая апелляция</b> — {appellant_user}\n"
            f"<blockquote>{conversationData[appellant_id]['msg1']}</blockquote>",
            reply_markup=kb.unbanKeyboard_(appellant_id)
        )


@adminside.callback_query(F.data.startswith("unbanAppealDecline_"))
async def cbUnbanAppealAccept(callback: CallbackQuery, state: FSMContext):
    appellant_id = int(callback.data.split("_")[-1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"

    global conversationData, activeAppeals
    del conversationData[appellant_id]



@adminside.callback_query(F.data.startswith("unbanAppealAccept_"))
async def cbUnbanAppealAccept(callback: CallbackQuery, state: FSMContext):
    appellant_id = int(callback.data.split("_")[-1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"

    global conversationData, activeAppeals

    activeAppeals[appellant_id] = {
        'admin_id': callback.from_user.id,
        'appellant_id': appellant_id,
    }
    
    if appellant_id not in conversationData:
        await callback.answer("❌ Аппеляция не найдена", show_alert=True)
        return

    await bot.send_message(
        chat_id=appellant_id,
        text="✅ <b>Апелляция была принята!</b> Администратор начал с Вами диалог."
    )

    await callback.message.edit_text(f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
                                     f"<blockquote>{conversationData[appellant_id]['msg1']}</blockquote>\n\n"
                                     f"<i>Принял {admin_user}</i>",
                                     reply_markup=kb.unbanKeyboardAcceptedActions_(appellant_id))