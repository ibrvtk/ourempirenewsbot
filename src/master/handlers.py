from config import (
    TOGGLE_OER, TOGGLE_CRM,
    LOG_ERRORS, LOG_OTHERS,
    SUPERADMIN, PREFIX
)

import oerChat.adminside as oerAdminside
# import oerChat.databases.scheme as oerDB
# from oerChat.databases.scheduler import schedulerAppealsTimeout

# import CRM_OE.userside as crmUserside
# import CRM_OE.adminside as crmAdminside
import CRM_OE.database.scheme as crmDB

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


rt = Router()



# Временная команда. Записывает пользователя в БД CRM_OE/database/players.db .
# Временная, так как БД ещё в разработке.
# Доступна только Суперадмину, что бы не записывать случайных пользователей.
# Позже функционал по идее будет перенесён в uniStart() .
@rt.message(F.user_id == SUPERADMIN, Command('db'))
async def cmdDb(message: Message) -> None:
    if TOGGLE_CRM:
        try:
            await crmDB.createUser(user_id=message.from_user.id)
            await message.reply("✅ Успех")
        except Exception as e:
            print(f"(XX) main.py: uniStart(): {e}.")

@rt.message(Command("start"))
@rt.message(F.text.lower() == "бот")
@rt.message(F.text.lower() == f"{PREFIX}бот")
async def uniStart(message: Message) -> None: # Временное решение. В будущем будет роадмап по командам бота.
    await message.reply("✅ На месте")


@rt.message(F.text.lower() == f"{PREFIX}отмена")
@rt.message(Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None: # Написано убого. Временное решение.
    user_id = message.from_user.id

    try: await state.clear()
    except: pass
    try: del oerAdminside.appealData[user_id]
    except: pass
    try: del oerAdminside.messagesData[user_id]
    except: pass

    await message.answer("✅ <b>Текущая операция отменена.</b>",
                             reply_markup=ReplyKeyboardRemove())