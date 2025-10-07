from config import bot, SUPERADMIN, ID_CRM_OE_ADMIN, ID_OERCHAT_ADMIN

from oerChat.app.adminside import adminside as oerAdminsideHandlers

from CRM_OE.app.userside import userside as crmUsersideHandlers
from CRM_OE.app.adminside import adminside as crmAdminsideHandlers
from CRM_OE.database.scheme import createTable, createUser

from asyncio import run

from aiogram import Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


dp = Dispatcher()
globalRouter = Router()



# Временная команда. Записывает пользователя в БД CRM_OE/database/players.db .
# Временная, так как БД ещё в разработке.
# Доступна только Суперадмину, что бы не записывать случайных пользователей.
# Позже функционал будет перенесён (как минимум) в uniStart() .
@globalRouter.message(F.user_id == SUPERADMIN, Command('db'))
async def cmdDb(message: Message):
    try:
        await createUser(user_id=message.from_user.id)
        await message.reply("✅ Успех")
    except Exception as e:
        print(f"(XXX) main.py: uniStart(): {e}.")


@globalRouter.message(F.user_id == SUPERADMIN, Command("start"))
@globalRouter.message(F.user_id == SUPERADMIN, F.text.lower() == "бот")
async def uniStart(message: Message):
    await message.answer("✅ На месте")


@globalRouter.message(Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ <b>Текущая операция отменена.</b>",
                             reply_markup=ReplyKeyboardRemove())



async def main():
    dp.include_router(globalRouter)

    dp.include_router(oerAdminsideHandlers)

    dp.include_router(crmUsersideHandlers)
    dp.include_router(crmAdminsideHandlers)

    await createTable()

    print("(V) main.py: start(): успех.")
    ADMIN_CHATS = [ID_OERCHAT_ADMIN, ID_CRM_OE_ADMIN]
    for chat in ADMIN_CHATS:
        await bot.send_message(
            chat_id=chat,
            text="<code>hola amigos por favor</code>"
        )
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"(XXX) main.py: Ошибка при запуске проекта: {e}")