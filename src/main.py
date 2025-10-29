from config import (
    BOT,
    TOGGLE_OER, TOGGLE_CRM,
    LOG_OTHERS,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_BOT_THREAD,
    ID_CRM_OE_ADMIN, ID_CRM_OE_ADMIN_BOT_THREAD
)

import master.handlers as mHandlers

import oerChat.adminside as oerAdminside
import oerChat.databases.scheme as oerDB
from oerChat.databases.scheduler import schedulerAppealsTimeout

import CRM_OE.userside as crmUserside
import CRM_OE.adminside as crmAdminside
import CRM_OE.database.scheme as crmDB

from asyncio import create_task, run

from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest


dp = Dispatcher()



async def main() -> None:
    dp.include_router(mHandlers.rt)
    print("(i) Запуск бота: Глобальный обработчик подключен.") if LOG_OTHERS else None

    ADMIN_CHATS = []
    if TOGGLE_OER:
        dp.include_router(oerAdminside.rt)
        print("(i) Запуск бота: oer: Админский обработчик подключен.") if LOG_OTHERS else None
        await oerDB.createTableAppeals()
        create_task(schedulerAppealsTimeout())
        print("(i) Запуск бота: oer: БД подключена.") if LOG_OTHERS else None
        ADMIN_CHATS.append((ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_BOT_THREAD))
        print("(V) Запуск бота: oer: Полностью подключен.")

    if TOGGLE_CRM:
        dp.include_router(crmUserside.rt)
        print("(i) Запуск бота: crm: Пользовательский обработчик подключен.") if LOG_OTHERS else None
        dp.include_router(crmAdminside.rt)
        print("(i) Запуск бота: crm: Админский обработчик подключен.") if LOG_OTHERS else None
        await crmDB.createTable()
        print("(i) Запуск бота: crm: БД подключена.") if LOG_OTHERS else None
        ADMIN_CHATS.append((ID_CRM_OE_ADMIN, ID_CRM_OE_ADMIN_BOT_THREAD))
        print("(V) Запуск бота: crm: полностью подключен.")

    for chat_id, topic_id in ADMIN_CHATS:
        await BOT.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text="<code>hola amigos por favor</code>"
        )
        
    print("(V) Запуск бота: Успех.")
    # await bot.delete_webhook(drop_pending_updates=True) # Будь ты проклят, PuTTY.
    await dp.start_polling(BOT)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"(XX) main.py: Ошибка при запуске: {e}.")