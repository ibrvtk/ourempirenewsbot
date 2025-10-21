from config import (
    bot, logOther,
    oerToggle, crmToggle,
    PREFIX, SUPERADMIN,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_APPEALS_THREAD,
    ID_CRM_OE_ADMIN
)

import oerChat.adminside as oerAdminside
import oerChat.databases.scheme as oerDB
from oerChat.databases.scheduler import schedulerAppealsTimeout

import CRM_OE.userside as crmUserside
import CRM_OE.adminside as crmAdminside
import CRM_OE.database.scheme as crmDB

from asyncio import create_task, run

from aiogram import Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


dp = Dispatcher()
rt = Router()



# Временная команда. Записывает пользователя в БД CRM_OE/database/players.db .
# Временная, так как БД ещё в разработке.
# Доступна только Суперадмину, что бы не записывать случайных пользователей.
# Позже функционал будет перенесён (как минимум) в uniStart() .
@rt.message(F.user_id == SUPERADMIN, Command('db'))
async def cmdDb(message: Message) -> None:
    if crmToggle:
        try:
            await crmDB.createUser(user_id=message.from_user.id)
            await message.reply("✅ Успех")
        except Exception as e:
            print(f"(XX) main.py: uniStart(): {e}.")


@rt.message(Command("start"))
@rt.message(F.text.lower() == "бот")
@rt.message(F.text.lower() == f"{PREFIX}бот")
async def uniStart(message: Message) -> None:
    await message.reply("✅ На месте")


@rt.message(Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None: # Написано убого. Временное решение.
    try: await state.clear()
    except: pass
    try: oerAdminside.appealData.pop(message.from_user.id, None)
    except: pass
    try: oerAdminside.messagesData.pop(message.from_user.id, None)
    except: pass

    await message.answer("✅ <b>Текущая операция отменена.</b>",
                             reply_markup=ReplyKeyboardRemove())



async def main() -> None:
    dp.include_router(rt)
    print("(i) main.py: Глобальный обработчик подключен.") if logOther else None
    ADMIN_CHATS = []

    if oerToggle:
        dp.include_router(oerAdminside.rt)
        print("(i) main.py: oer админский обработчик подключен.") if logOther else None
        await oerDB.createTableAppeals()
        create_task(schedulerAppealsTimeout())
        print("(i) main.py: oer БД подключена.") if logOther else None
        ADMIN_CHATS.append(ID_OERCHAT_ADMIN); print("(i) oer подключен.")

    if crmToggle:
        dp.include_router(crmUserside.userside)
        print("(i) main.py: crm пользовательский обработчик подключен.") if logOther else None
        dp.include_router(crmAdminside.adminside)
        print("(i) main.py: crm админский обработчик подключен.") if logOther else None
        await crmDB.createTable()
        print("(i) main.py: crm БД подключена.") if logOther else None
        ADMIN_CHATS.append(ID_CRM_OE_ADMIN); print("(i) crm подключен.")

    for chat in ADMIN_CHATS:
        await bot.send_message(
            chat_id=chat,
            message_thread_id=ID_OERCHAT_ADMIN_APPEALS_THREAD if chat == ID_OERCHAT_ADMIN else None,
            text="<code>hola amigos por favor</code>"
        )
        
    print("(V) main.py: Бот успешно запустился.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"(XX) main.py: Ошибка при запуске: {e}.")