from config import bot, ID_CRM_OE, ID_CRM_OE_ADMIN
from CRM_OE.database.scheme import createTable

from CRM_OE.app.handlers import handlers as crmHandlers

import asyncio

from aiogram import Dispatcher, Router, F
from aiogram.types import Message


dp = Dispatcher()
globalRouter = Router()



@globalRouter.message(F.text.lower() == "бот")
async def textBotCheck(message: Message):
    await message.answer("✅ На месте")



async def start():
    dp.include_router(globalRouter)
    dp.include_router(crmHandlers)

    await createTable()

    print("(V) main.py: start(): успех.")
    await bot.send_message(
        chat_id=ID_CRM_OE_ADMIN,
        text="<code>hola amigos por favor</code>"
    )
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("(V) main.py: shutdown(): успех.")
        bot.send_message(
            chat_id=ID_CRM_OE_ADMIN,
            text="<code>Change the world. My final message. Goodbye.</code>"
        )
    except Exception as e:
        print(f"(XXX) main.py: {e}")