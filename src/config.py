from dotenv import load_dotenv; load_dotenv()
from os import getenv

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


TOKEN = getenv('TOKEN')
ID = int(getenv('ID'))

BOT = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
PREFIX = getenv('PREFIX')



'''Логгирование в терминале'''
LOG_ERRORS_RAW = getenv('LOG_ERRORS'); LOG_ERRORS = False
if LOG_ERRORS_RAW == "True": LOG_ERRORS = True # Логгирование ошибок (X). Непредвиденные ошибки (XX) логируются даже при выключенном параметре.
LOG_OTHERS_RAW = getenv('LOG_OTHERS'); LOG_OTHERS = False
if LOG_OTHERS_RAW == "True": LOG_OTHERS = True # Логгирование информационных сообщений (i), о создании новых процессов (+) и итогах функций.
''''''

'''ВКЛ/ВЫКЛ работу бота в определённых чатах'''
TOGGLE_OER_RAW = getenv('TOGGLE_OER'); TOGGLE_OER = False
if TOGGLE_OER_RAW == "True": TOGGLE_OER = True # @oerChat (oerChat/*)
TOGGLE_CRM_RAW = getenv('TOGGLE_CRM'); TOGGLE_CRM = False
if TOGGLE_CRM_RAW == "True": TOGGLE_CRM = True # @CRM_OE (CRM_OE/*)
''''''


# Суперадмин может без прав в боте (БД) управлять им в любом месте.
SUPERADMIN = int(getenv('SUPERADMIN'))
# Если нужен список суперадминов закомментировать строку выше и раскомментировать две ниже:
# SUPERADMIN_RAW = getenv('SUPERADMIN_ARRAY')
# SUPERADMIN = [int(admin_id.strip()) for admin_id in SUPERADMIN_ARRAY.split(',')]


'''Айди чатов, в которых бот работает'''
# Команды, вводимые только в админ чате (*ADMIN*), выполняются без проверки на наличие роли админа,
# так что будьте осторожнее с тем, кого Вы добавляте в чат админов.
ID_OERCHAT = int(getenv('ID_OERCHAT'))
ID_OERCHAT_ADMIN = int(getenv('ID_OERCHAT_ADMIN'))
ID_OERCHAT_ADMIN_BOT_THREAD = int(getenv('ID_OERCHAT_ADMIN_BOT_THREAD'))

ID_CRM_OE = int(getenv('ID_CRM_OE'))
ID_CRM_OE_ADMIN = int(getenv('ID_CRM_OE_ADMIN'))
ID_CRM_OE_ADMIN_BOT_THREAD = int(getenv('ID_CRM_OE_ADMIN_BOT_THREAD'))
ID_CRM_OE_COUNTRIES_THREAD = int(getenv('ID_CRM_OE_COUNTRIES_THREAD'))
ID_CRM_OE_NONOFFTOP_THREADS_RAW = getenv('ID_CRM_OE_NONOFFTOP_THREADS')
ID_CRM_OE_NONOFFTOP_THREADS = [int(thread_id.strip()) for thread_id in ID_CRM_OE_NONOFFTOP_THREADS_RAW.split(',')]
ID_CRM_OE_ONLYPLAYERS_THREADS = getenv('ID_CRM_OE_ONLYPLAYERS_THREADS')
ID_CRM_OE_ONLYPLAYERS_THREADS = [int(thread_id.strip()) for thread_id in ID_CRM_OE_ONLYPLAYERS_THREADS.split(',')]
''''''

'''Пути к базам данных'''
DB_OER_USERS_PATH = getenv('DB_OER_USERS_PATH')
DB_OER_APPEALS_PATH = getenv('DB_OER_APPEALS_PATH')

DB_CRM_PATH = getenv('DB_CRM_PLAYERS_PATH')
''''''