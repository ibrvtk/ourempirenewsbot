from config import bot, CRM_OE

#from oerChat.app.handlers import handlers as orcHandlers

from CRM_OE.app.handlers import handlers as crmHandlers
#from CRM_OE.app.callbacks import callbacks as crmCallbacks

import asyncio

from aiogram import Dispatcher


dp = Dispatcher()

        

async def start():
    #dp.include_router(orcHandlers)

    dp.include_router(crmHandlers)
    #dp.include_router(crmCallbacks)

    print("✅")
    await bot.send_message(
        chat_id=CRM_OE,
        message_thread_id=54,
        text="<code>hola amigos por favor</code>"
    )
    
    await dp.start_polling(bot)

async def shutdown():
    print("💤")
    await bot.send_message(
        chat_id=CRM_OE,
        message_thread_id=54,
        text="<code>Change the world. My final message. Goodbye.</code>"
    )

if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
    except Exception as e:
        print(f"❗ {e}")