from config import bot, oerToggle, crmToggle, SUPERADMIN, ID_CRM_OE_ADMIN, ID_OERCHAT_ADMIN

from oerChat.app.adminside import adminside as oerAdminsideHandlers

from CRM_OE.app.userside import userside as crmUsersideHandlers
from CRM_OE.app.adminside import adminside as crmAdminsideHandlers
import CRM_OE.database.scheme as crmDB

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
    if crmToggle:
        try:
            await crmDB.createUser(user_id=message.from_user.id)
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

    dp.include_router(oerAdminsideHandlers) if oerToggle else None

    dp.include_router(crmUsersideHandlers)  if crmToggle else None
    dp.include_router(crmAdminsideHandlers) if crmToggle else None
    await crmDB.createTable()               if crmToggle else None

    ADMIN_CHATS = []
    if oerToggle: ADMIN_CHATS.append(ID_OERCHAT_ADMIN); print("(i) oer включен.")
    if crmToggle: ADMIN_CHATS.append(ID_CRM_OE_ADMIN); print("(i) crm включен.")
    for chat in ADMIN_CHATS:
        await bot.send_message(
            chat_id=chat,
            text="<code>hola amigos por favor</code>"
        )
        
    print("(V) main.py: start(): успех.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"(XXX) main.py: Ошибка при запуске проекта: {e}")