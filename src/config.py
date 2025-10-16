from dotenv import load_dotenv
from os import getenv
from asyncio import sleep

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message


load_dotenv()
TOKEN = getenv('TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

# Логгирование в терминале:
# logCommands  = True # Все поступающие команды.
# logCallbacks = True # Все поступающие колбэки.
logOther     = True # Логгирование всего остального (F.text, функции и т. д.).
logErrors    = True # Все ошибки. Критические ошибки (XXX) логируются даже если этот параметр False.

# ВКЛ/ВЫКЛ работу бота в определённых чатах:
oerToggle = True # @oerChat (oerChat/*)
crmToggle = False # @CRM_OE (CRM_OE/*)



async def delayMsgDelete(message: Message, delay: int) -> None:
    await sleep(delay)
    try:
        await message.delete()
        user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"
        placeholderText = f"{message.message_thread_id}: удалён оффтоп" if message.chat.id == ID_CRM_OE else "удалено сообщение по отложке"
        if delay < 60: time_display = f"{delay} секунд"
        else: delay_minutes = delay // 60; time_display = f"{delay_minutes} минут"
        print(f"(V) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText} от {user} (прошло {time_display} минут).") if logOther else None

    except Exception as e:
        user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"
        placeholderText = f"{message.message_thread_id}: оффтоп  от {user} был удалён:" if message.chat.id == ID_CRM_OE else f"отложенное удаление сообщения от {user} не произошло:"
        print(f"(X) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText} {e}.") if logErrors else None



# Суперадмин может без прав в боте (БД) управлять им в любом месте.
SUPERADMIN = int(getenv('SUPERADMIN'))
# Захаркоденый список суперадминов.
# SUPERADMIN = (-100, -100,)


# DB_OER_USERS_PATH = getenv('DB_OER_USERS_PATH')
DB_OER_APPEALS_PATH = getenv('DB_OER_APPEALS_PATH')

DB_CRM_PATH = getenv('DB_CRM_PLAYERS_PATH')


# Команды, вводимые только в админ чате (*_ADMIN), выполняются без проверки на наличие роли админа,
# так что будьте осторожнее с тем, кого Вы добавляте в чат админов.
ID_OERCHAT = int(getenv('ID_OERCHAT'))
ID_OERCHAT_ADMIN = int(getenv('ID_OERCHAT_ADMIN'))
ID_OERCHAT_ADMIN_APPEALS_THREAD = int(getenv('ID_OERCHAT_ADMIN_APPEALS_THREAD'))

ID_CRM_OE = int(getenv('ID_CRM_OE'))
ID_CRM_OE_ADMIN = int(getenv('ID_CRM_OE_ADMIN'))