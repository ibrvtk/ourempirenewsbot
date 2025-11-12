from config import (
    bot,
    TOGGLE_OER, TOGGLE_CRM,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_TERMINAL_THREAD
)

from master.handlers import rt as mHandlersRouter
from master.logging import logOther

from oer.admin.handlers import rt as oerAdminHandlersRouter
from oer.admin.callbacks import rt as oerAdminCallbacksRouter
from oer.database.scheme import createTableAppeals
from oer.database.scheduler import schedulerAppealsTimeout

from crm.user.handlers import rt as crmUserHandlersRouter
from crm.admin.handlers import rt as crmAdminHandlersRouter
from crm.database.scheme import createTable

from asyncio import create_task, run
from aiohttp import ClientSession
from datetime import datetime

from aiogram import Dispatcher


dp = Dispatcher()



async def main() -> None:
    '''Функция запуска бота.'''
    session = ClientSession()
    try:
        dp.include_router(mHandlersRouter)
        await logOther("(V) Запуск бота: master: Полностью подключен.")

        if TOGGLE_OER:
            dp.include_router(oerAdminHandlersRouter)
            dp.include_router(oerAdminCallbacksRouter)
            await logOther("(i) Запуск бота: oer: admin подключен.")
            await createTableAppeals()
            create_task(schedulerAppealsTimeout())
            await logOther("(i) Запуск бота: oer: БД подключена.")
            await logOther("(V) Запуск бота: oer: Полностью подключен.")

        if TOGGLE_CRM:
            dp.include_router(crmAdminHandlersRouter)
            await logOther("(i) Запуск бота: crm: admin подключен.")
            dp.include_router(crmUserHandlersRouter)
            await logOther("(i) Запуск бота: crm: user подключен.")
            await createTable()
            await logOther("(V) Запуск бота: crm: Полностью подключен, включая БД.")

        await bot.send_message(
            chat_id=ID_OERCHAT_ADMIN,
            message_thread_id=ID_OERCHAT_ADMIN_TERMINAL_THREAD,
            text="✅ <b>Запуск бота:</b> Успех."
        )

        await logOther("(V) Запуск бота: Успех.")
        # await bot.delete_webhook(drop_pending_updates=True) # Будь ты проклят, PuTTY.
        await dp.start_polling(bot)

    finally:
        await session.close()

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        timestamp = datetime.now().strftime("%H:%M")
        print(f"[{timestamp}] (X) {e}.")