from config import bot, ID_CRM_OE_ADMIN, ID_OERCHAT_ADMIN

from CRM_OE.app.userside import userside as crmUsersideHandlers
from CRM_OE.app.adminside import adminside as crmAdminsideHandlers
from CRM_OE.database.scheme import createTable, createUser

import asyncio

from aiogram import Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command


dp = Dispatcher()
globalRouter = Router()



@globalRouter.message(Command('db')) # Временная команда.
async def cmdDb(message: Message):
    try:
        await createUser(user_id=message.from_user.id)
        await message.reply("✅ Успех")
    except Exception as e:
        print(f"(XXX) main.py: uniStart(): {e}.")


@globalRouter.message(Command("start"))
@globalRouter.message(F.text.lower() == "бот")
async def uniStart(message: Message):
    await message.answer("✅ На месте",
                         reply_markup=ReplyKeyboardRemove())



async def start():
    dp.include_router(globalRouter)

    dp.include_router(crmUsersideHandlers)
    dp.include_router(crmAdminsideHandlers)

    await createTable()

    print("(V) main.py: start(): успех.")
    ADMIN_CHATS = [ID_OERCHAT_ADMIN, ID_CRM_OE_ADMIN]
    for i in ADMIN_CHATS:
        await bot.send_message(
            chat_id=i,
            text="<code>hola amigos por favor</code>"
        )
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(start())
    except Exception as e:
        print(f"(XXX) main.py: {e}")