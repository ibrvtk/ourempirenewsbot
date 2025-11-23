from config import (
    ID_CRM_OE_ADMIN,
    PREFIX, SUPERADMIN
)

from oer.admin.master import unbanWriteAppealIdInDB as oerUnbanWriteAppealIdInDB

from crm.database.scheme import readUser as crmReadUser

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandObject


rt = Router()



# @rt.message(F.chat.type == "private", Command("start"))
# async def cmdStart(message: Message, command: CommandObject) -> None:
#     await message.answer(f"")

# @rt.message(F.chat.type == "private", Command('developer_info'))
# async def cmdDeveloperInfo(message: Message):


@rt.message(F.text.lower() == "бот")
@rt.message(F.text.lower() == f"{PREFIX}бот")
async def fcmdCheck(message: Message) -> None:
    await message.reply("✅ На месте")


@rt.message(F.from_user.id.in_(SUPERADMIN), Command("echo"))
async def cmdEcho(message: Message, command: CommandObject):
    if command.args is None:
        await message.delete()
        return
    
    await message.delete()
    await message.answer(command.args)


@rt.message(F.text.lower() == f"{PREFIX}отмена")
@rt.message(Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None: # Написано убого. Временное решение.
    user_id = message.from_user.id

    try: await oerUnbanWriteAppealIdInDB(appellant_id=user_id, state=state)
    except: pass
    try: await state.clear()
    except: pass
    await message.answer("✅ <b>Текущая операция отменена.</b>",
                            reply_markup=ReplyKeyboardRemove())


@rt.message(Command('help'))
async def cmdHelp(message: Message, command: CommandObject) -> None:
    if command.args is None:
        await message.reply("Coming soon")
        return
    
    args = command.args.split()

    user_id = message.from_user.id

    if message.chat.id == ID_CRM_OE_ADMIN:
        user_data = await crmReadUser(user_id)
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
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [название_страны] [флаг] [капитулирован?]**</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение, а двойная от 0 до 1, что является True и False. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n\n{hashtags}")

                case 22:
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [название_страны] [флаг]</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n\n{hashtags}")
                    
                case 5:
                    nano = "📝 <code>/user [изменить/update/nano] [TG-ID]* [админка]* [репутация]* [название страны] [флаг] [капитулирован?]** [влияние]*</code> — изменение данных, " \
                           f"где звёздочка обозначает цифровое значение, а двойная от 0 до 1, что является True и False. {nano_outro}"
                    await message.reply(f"{title}\n{description}\n\n{touch}\n{cat}\n{nano}\n{rm}\n\n{hashtags}")

                case _:
                    await message.reply(f"{title}\n{description}\n\n{hashtags}")


@rt.message(Command("id"))
@rt.message(F.text.lower() == f"{PREFIX}id")
@rt.message(F.text.lower() == "id")
@rt.message(F.text.lower() == f"{PREFIX}айди")
@rt.message(F.text.lower() == "айди")
@rt.message(F.text.lower() == f"{PREFIX}ид")
@rt.message(F.text.lower() == "ид")
async def cmdId(message: Message) -> None:
    if not message.reply_to_message:
        await message.reply(f"<code>{message.from_user.id}</code>")
        return
    
    await message.reply(f"<code>{message.reply_to_message.from_user.id}</code>")


@rt.message(F.from_user.id.in_(SUPERADMIN), F.text.lower() == f"{PREFIX}суперадмины")
async def fcmdSuperadmins(message: Message):
    await message.reply(f"{SUPERADMIN}")