from config import (
    bot,
    TOGGLE_OER, TOGGLE_CRM,
    ID_OERCHAT_ADMIN, ID_OERCHAT_ADMIN_TERMINAL_THREAD
)

from master.handlers import rt as mHandlersRouter
from master.logging import logOther, logError

from oer.admin.handlers import rt as oerAdminHandlersRouter
from oer.admin.callbacks import rt as oerAdminCallbacksRouter
from oer.databases.scheme import createTableAppeals
from oer.databases.scheduler import schedulerAppealsTimeout

from crm.user.handlers import rt as crmUserHandlersRouter
from crm.admin.handlers import rt as crmAdminHandlersRouter
from crm.database.scheme import createTable

from asyncio import create_task, run

from aiogram import Dispatcher


dp = Dispatcher()



async def main() -> None:
    dp.include_router(mHandlersRouter)
    await logOther("(i) Запуск бота: master: handlers роутер подключен.")

    if TOGGLE_OER:
        dp.include_router(oerAdminHandlersRouter)
        dp.include_router(oerAdminCallbacksRouter)
        await logOther("(i) Запуск бота: oer: admin полностью подключен.")
        await createTableAppeals()
        create_task(schedulerAppealsTimeout())
        await logOther("(i) Запуск бота: oer: БД подключена.")
        await logOther("(V) Запуск бота: oer: Полностью подключен.")

    if TOGGLE_CRM:
        dp.include_router(crmAdminHandlersRouter)
        await logOther("(i) Запуск бота: crm: admin обработчик подключен.")
        dp.include_router(crmUserHandlersRouter)
        await logOther("(i) Запуск бота: crm: user обработчик подключен.")
        await createTable()
        await logOther("(V) Запуск бота: crm: полностью подключен, включая БД.")

    await bot.send_message(
        chat_id=ID_OERCHAT_ADMIN,
        message_thread_id=ID_OERCHAT_ADMIN_TERMINAL_THREAD,
        text="✅ <b>Запуск бота:</b> Успех."
    )

    await logOther("(V) Запуск бота: Успех.")
    # await bot.delete_webhook(drop_pending_updates=True) # Будь ты проклят, PuTTY.
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        run(logError(f"Запуск бота: Ошибка: {e}."))