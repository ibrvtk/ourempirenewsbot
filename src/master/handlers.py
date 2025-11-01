from config import (
    TOGGLE_OER, TOGGLE_CRM,
    #ID_OERCHAT_ADMIN,
    ID_CRM_OE_ADMIN,
    LOG_ERRORS,# LOG_OTHERS,
    SUPERADMIN, PREFIX
)

import oerChat.adminside as oerAdminside
# import oerChat.databases.scheme as oerDB
# from oerChat.databases.scheduler import schedulerAppealsTimeout

# import CRM_OE.userside as crmUserside
# import CRM_OE.adminside as crmAdminside
import CRM_OE.database.scheme as crmDB

from re import compile

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandObject


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
            return

# @rt.message(Command("start"))
# async def cmdStart

@rt.message(F.text.lower() == "бот")
@rt.message(F.text.lower() == f"{PREFIX}бот")
async def fcmdCheck(message: Message) -> None: # Временное решение. В будущем будет роадмап по командам бота.
    await message.reply("✅ На месте")


@rt.message(F.text.lower() == f"{PREFIX}отмена")
@rt.message(Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None: # Написано убого. Временное решение.
    user_id = message.from_user.id

    try:
        await oerAdminside.unbanWriteAppealIdInDB(user_id, state)
        await state.clear()
        await message.answer("✅ <b>Текущая операция отменена.</b>",
                                reply_markup=ReplyKeyboardRemove())
        
    except Exception as e:
        if int(e) == user_id:
            print(f"(X) master/handlers: cmdCancel(): У {user_id} нечего отменять.") if LOG_ERRORS else None
        else:
            print(f"(XX) master/handlers: cmdCancel(): {e}.")
        return


@rt.message(Command('help'))
async def cmd(message: Message, command: CommandObject):
    if command.args is None:
        await message.reply("Coming soon")
        return
    
    args = command.args.split()

    user_id = message.from_user.id

    if message.chat.id == ID_CRM_OE_ADMIN:
        user_data = await crmDB.readUser(user_id)
        if not user_data: return

        if args[0] == "user":
            title =       "🗃️ <b>Команда <code>user</code></b>"
            description = "БД — база данных. Она хранит в себе данные всех игроков и тех, кто когда-то был им." \
                          "Она содержит в себе информацию об уровне админки, количестве очков, репутации, " \
                          "название страны, флаг страны, жив ли игрок " \
                          "и информацию о ходе (текст, медиафайлы, отправлен ли)."
            touch =       "🛄 <code>/user [создать/добавить/create/add/touch] [TG-ID]</code> — добавление в БД."
            cat =         "🛂 <code>/user [прочитать/read/cat] [TG-ID]</code> — список данных."
            nano_outro =  "Важно прописать все параметры, даже если Вы их не меняете."
            rm =          "🗑️ <code>/user [удалить/delete/rm] [TG-ID]</code> — удаление из БД."
            hashtags =    "<i>ЦРМ, Админская команда, БД</i>"

            match int(user_data[1]):
                case 21:
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [название_страны] [флаг]</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n\n{hashtags}")

                case 22:
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [название_страны] [флаг] [капитулирован?]**</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение, а двойная от 0 до 1, что является True и False. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n\n{hashtags}")
                    
                case 5:
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [админка]* [очки]* [репутация]* [название страны] [флаг] [капитулирован?]**</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение, а двойная от 0 до 1, что является True и False. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n{rm}\n\n{hashtags}")

                case _:
                    await message.reply(f"{title}\n{description}\n\n{hashtags}")