from config import bot, logErrors, ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_APPEALS_THREAD
from oerChat.keyboards import unbanKeyboard_, unbanKeyboardAcceptedActions_
from oerChat.databases.appeals import createUser, readUser, updateUser

from dataclasses import dataclass
from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


adminside = Router()

conversationData = {}



# /unban:
# appellant — подающий апелляцию, admin — принимающий.
class fsmUnbanSendAppeal(StatesGroup):
    text = State() # Истории переписки. Значение сливается в conversationData[appellant_id][f'message_{msgCount}'], а после обнуляется.

@dataclass
class ConversationDataclass:
    appellant_id: int = 0
    appellant_user: str = ""
    admin_id: int | None = None
    admin_user: str | None = None
    appeal_id: str = ""
    appeal_status: bool = True
    admin_message_id: int | None = None
    appellant_message_count: int = 0


async def appealStatusCheck(appellant_id: int, state: FSMContext) -> bool:
    global conversationData
    
    if appellant_id not in conversationData:
        await state.clear()
        return False
    
    appeal_status = conversationData[appellant_id].appeal_status
    
    if not appeal_status:
        await state.clear()
        del conversationData[appellant_id]
        return False
    
    return True

async def appealIdWrite(appellant_id: int, state: FSMContext) -> None:
    appellant_data = await readUser(appellant_id)
    global conversationData
    appeal_id = conversationData[appellant_id].appeal_id

    if appellant_data[1] == "None":
        appeal_id_for_database = f"{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)
    else:
        appeal_id_for_database = f"{appellant_data[1]}{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)

    conversationData[appellant_id].appeal_status = False; await appealStatusCheck(appellant_id, state)


# Непосредственный ввод команды /unban
@adminside.message(F.chat.type == "private", Command("unban"))
async def cmdUnban(message: Message, state: FSMContext) -> None:
    appellant_id = message.from_user.id
    appellant_user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} (<code>{message.from_user.id}</code>)"
    await createUser(appellant_id)
    appellant_data = await readUser(appellant_id)
    global conversationData

    if appellant_data[2] > datetime.now().timestamp():
        timeout_end = datetime.fromtimestamp(appellant_data[2])
        await message.reply(f"📵 У вас активен таймаут до <b>{timeout_end.strftime('%d.%m.%Y %H:%M')}</b>.")
        return

    if appellant_id in conversationData:
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

    conversationData[appellant_id] = ConversationDataclass(
        appellant_id = appellant_id,
        appellant_user = appellant_user,
        appeal_id = appeal_id
    )

    await state.set_state(fsmUnbanSendAppeal.text)

    await message.answer(f"🆘 <b>Апелляция на разбан</b> — {appellant_user}\n"
                        "Ваше следующее сообщение будет переслано в чат администрации, откуда с Вами будет производиться общение.\n"
                        "Опишите за что Вас забанили <i>(если знаете)</i> и почему Вы нарушали.\n\n"
                        "<i>Для отмены напишите /cancel.</i>")
    
@adminside.message(fsmUnbanSendAppeal.text)
async def fsmUnbanSendAppealText(message: Message, state: FSMContext) -> None:
    appellant_id = message.from_user.id
    appellant_user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} (<code>{message.from_user.id}</code>)"
    global conversationData

    await appealStatusCheck(appellant_id, state)

    if not message.text:
        await state.clear()
        del conversationData[appellant_id]
        await message.reply("❌ <b>Ошибка.</b> В данный момент бот не принимает медиафайлы. Повторите отправку /unban.")
        return

    conversationData[appellant_id]['appellant_message_count'] += 1
    appellant_message_count = conversationData[appellant_id]['appellant_message_count']
    message_ = f"message_{appellant_message_count}"

    match appellant_message_count:
        # Если это первое сообщение человека (отправка апелляции).
        case 1:
            conversationData[appellant_id][message_] = message.text

            await message.reply("✅ <b>Апелляция была отправлена.</b> Ожидайте ответа от модерации.")

            message_id = await bot.send_message(
                chat_id=ID_OERCHAT_ADMIN,
                message_thread_id=ID_OERCHAT_ADMIN_APPEALS_THREAD,
                text=f"🆘 <b>Новая апелляция</b> — {appellant_user}\n"
                f"<blockquote>{conversationData[appellant_id][message_]}</blockquote>",
                reply_markup=unbanKeyboard_(conversationData[appellant_id]['appeal_id'])
            )
            conversationData[appellant_id]['admin_message_id'] = message_id.message_id

        # Если апелляция уже принята и человек ведёт переписку.
        case _:
            conversationData[appellant_id][message_] = message.text
            appellant_message_id = message.message_id

            await bot.set_message_reaction(
                chat_id=appellant_id,
                message_id=appellant_message_id,
                reaction=[{"type": "emoji", "emoji": "👍"}]
            )

            await bot.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=conversationData[appellant_id]['admin_message_id'],
                text=f"🆘 <b>Апелляция</b> — {appellant_user}\n"
                f"<blockquote>{conversationData[appellant_id][message_]}</blockquote>\n\n"
                f"<i>Принят {conversationData[appellant_id]['admin_user']}</i>",
                reply_markup=unbanKeyboardAcceptedActions_(conversationData[appellant_id]['appeal_id'])
            )


# Апелляция принята.
@adminside.callback_query(F.data.startswith("unbanAppealAccept_"))
async def cbUnbanAppealAccept(callback: CallbackQuery) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    conversationData[appellant_id]['admin_id'] = callback.from_user.id
    conversationData[appellant_id]['admin_user'] = admin_user

    await bot.send_message(
        chat_id=appellant_id,
        text="✅ <b>Апелляция была принята!</b> У Вас начался диалог с администратором <i>(через бота)</i>."
    )

    await callback.message.edit_text(f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
                                    f"<blockquote>{conversationData[appellant_id]['message_1']}</blockquote>\n\n"
                                    f"<i>Принят {admin_user}</i>",
                                    reply_markup=unbanKeyboardAcceptedActions_(conversationData[appellant_id]['appeal_id']))
    # Дискуссия продолжается в fsmUnbanSendAppealText: match msgCount: case _ .
    
# Апелляция отклонена.
@adminside.callback_query(F.data.startswith("unbanAppealDecline_"))
async def cbUnbanAppealDecline(callback: CallbackQuery, state: FSMContext) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    await appealIdWrite(appellant_id)

    conversationData[appellant_id]['admin_id'] = callback.from_user.id
    conversationData[appellant_id]['admin_user'] = admin_user

    await bot.send_message(
        chat_id=appellant_id,
        text="🗑 <b>Вашу апелляцию отклонили.</b>"
    )

    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=conversationData[appellant_id]['admin_message_id'],
        text=f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
        f"<blockquote>{conversationData[appellant_id][f'message_1']}</blockquote>\n\n"
        f"<i>Отклонён {admin_user}</i>",
        reply_markup=None
    )

    conversationData[appellant_id]['appeal_status'] = False; await appealStatusCheck(appellant_id, state)

# Выдан таймаут.
class fsmTimeoutSetTime(StatesGroup):
    time = State()

@adminside.callback_query(F.data.startswith("unbanAppealTimeout_"))
async def unbanAppealTimeout(callback: CallbackQuery, state: FSMContext) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    conversationData[appellant_id]['admin_id'] = callback.from_user.id
    conversationData[appellant_id]['admin_user'] = admin_user

    await state.clear()
    await state.set_state(fsmTimeoutSetTime.time)
    await state.update_data(appellant_id=appellant_id, admin_user=admin_user)

    await callback.message.edit_text("⏱️ Напишите в <b>следующем</b> сообщении время в <b>секундах,</b> "
                                    "на которое этот человек лишится возможности контактировать с ботом. <b>Просто число.</b>")
    
@adminside.message(fsmTimeoutSetTime.time)
async def fsmTimeoutSetTimeTime(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    appellant_id = data.get('appellant_id')
    admin_user = data.get('admin_user')
    global conversationData

    if not appellant_id or appellant_id not in conversationData:
        return

    if message.from_user.id != conversationData[appellant_id]['admin_id']:
        return

    try:
        time_seconds = int(message.text.strip())

        if time_seconds <= 0:
            await message.reply("❌ Время должно быть положительным числом!")
            return

        timeout_end = int(datetime.now().timestamp()) + time_seconds
        
        if time_seconds < 60: time_display = f"{time_seconds} секунд"
        elif time_seconds < 3600: time_minutes = time_seconds // 60; time_display = f"{time_minutes} минут"
        else: time_hours = time_seconds // 3600; time_display = f"{time_hours} часов"
        
        await updateUser(appellant_id, timeout=timeout_end)

        await appealIdWrite(appellant_id)

        await bot.send_message(
            chat_id=appellant_id,
            text=f"📵 <b>Вам выдали таймаут на {time_display}.</b>"
        )

        await bot.edit_message_text(
            chat_id=ID_OERCHAT_ADMIN,
            message_id=conversationData[appellant_id]['admin_message_id'],
            text=f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
            f"<blockquote>{conversationData[appellant_id]['message_1']}</blockquote>\n\n"
            f"<i>{admin_user} выдал таймаут на {time_seconds} секунд</i>",
            reply_markup=None
        )

        conversationData[appellant_id]['appeal_status'] = False; await appealStatusCheck(appellant_id, state)


    except ValueError as e:
        await message.reply("❌ <b>Ошибка!</b> Нужно отправить секунды числом. Попробуйте снова.")
        print(f"(X) oerChat/adminside.py: fsmTimeoutSetTimeTime(): ValueError? — {e}.")
        return
    except Exception as e:
        await message.reply("❌ <b>Непредвиденная ошибка!</b> Проверьте существует ли апелляция и в правильном ли вы формате отправили секунды. Попробуйте снова.")
        print(f"(XX) oerChat/adminside.py: fsmTimeoutSetTimeTime(): {e}.")
        return


# В разбане разрешено.
@adminside.callback_query(F.data.startswith("unbanAppealAcceptUnban_"))
async def unbanAppealAcceptUnban(callback: CallbackQuery, state: FSMContext) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    if callback.from_user.id != conversationData[appellant_id]['admin_id']:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    await bot.send_message(
        chat_id=appellant_id,
        text="🎉 <b>Вы были разбанены!</b> Добро пожаловать. Снова."
    )

    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=conversationData[appellant_id]['admin_message_id'],
        text=f"🆘 <b>Решённая апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
        f"Принят {admin_user}"
        f"Итог: разбан",
        reply_markup=None
    )

    await state.clear()
    del conversationData[appellant_id]

# В разбане отказано.
@adminside.callback_query(F.data.startswith("unbanAppealDeclineUnban_"))
async def unbanAppealDeclineUnban(callback: CallbackQuery, state: FSMContext) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    await appealIdWrite(appellant_id)

    if callback.from_user.id != conversationData[appellant_id]['admin_id']:
        await callback.answer("🖕 Это не твоя апелляция!")
        return

    await bot.send_message(
        chat_id=appellant_id,
        text="❌ <b>Вам отказали в разбане.</b>"
    )

    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=conversationData[appellant_id]['admin_message_id'],
        text=f"🆘 <b>Решённая апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
        f"Принят {admin_user}\n"
        f"Итог: отказ",
        reply_markup=None
    )

    conversationData[appellant_id]['appeal_status'] = False; await appealStatusCheck(appellant_id, state)


# Прошлое сообщение в дискуссии.
@adminside.callback_query(F.data.startswith("unbanAppealHistoryPrev_"))
async def unbanAppealHistoryPrev(callback: CallbackQuery) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    if callback.from_user.id != conversationData[appellant_id]['admin_id']:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    conversationData[appellant_id]['appellant_message_count'] -= 1

    if conversationData[appellant_id]['appellant_message_count'] <= 0:
        conversationData[appellant_id]['appellant_message_count'] += 1
        await callback.answer("❌ Это первое сообщение")
        return
    
    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=conversationData[appellant_id]['admin_message_id'],
        text=f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
        f"<blockquote>{conversationData[appellant_id][f'message_{conversationData[appellant_id]['appellant_message_count']}']}</blockquote>\n\n"
        f"<i>Принят {admin_user}</i>",
        reply_markup=unbanKeyboardAcceptedActions_(conversationData[appellant_id]['appeal_id'])
    )

# Следующее сообщение в дискуссии.
@adminside.callback_query(F.data.startswith("unbanAppealHistoryNext_"))
async def unbanAppealHistoryNext(callback: CallbackQuery) -> None:
    appellant_id = int(callback.data.split("_")[1])
    admin_user = f"@{callback.from_user.username}" if callback.from_user.username else f"{callback.from_user.first_name} (<code>{callback.from_user.id}</code>)"
    appellant_data = await readUser(appellant_id)
    appeal_ids = appellant_data[1].split(", ")
    global conversationData

    if conversationData[appellant_id]['appeal_id'] in appeal_ids:
        await callback.answer("❓ Апелляция не найдена")
        return

    if callback.from_user.id != conversationData[appellant_id]['admin_id']:
        await callback.answer("🖕 Это не твоя апелляция!")
        return
    
    conversationData[appellant_id]['appellant_message_count'] += 1

    if f"message_{conversationData[appellant_id]['appellant_message_count']}" not in conversationData[appellant_id]:
        conversationData[appellant_id]['appellant_message_count'] -= 1
        await callback.answer("❌ Это последнее сообщение")
        return
    
    await bot.edit_message_text(
        chat_id=ID_OERCHAT_ADMIN,
        message_id=conversationData[appellant_id]['admin_message_id'],
        text=f"🆘 <b>Апелляция</b> — {conversationData[appellant_id]['appellant_user']}\n"
        f"<blockquote>{conversationData[appellant_id][f'message_{conversationData[appellant_id]['appellant_message_count']}']}</blockquote>\n\n"
        f"<i>Принят {admin_user}</i>",
        reply_markup=unbanKeyboardAcceptedActions_(conversationData[appellant_id]['appeal_id'])
    )