from config import (
    bot,
    logErrorsBool,
    ID_OERCHAT_ADMIN
)

from oer.databases.appeals import readUser, updateUser

from asyncio import sleep
from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


'''
В этом фале храняться глобальные переменные, функции, датаклассы и так далее,
неоходимые для работы некоторых команд, раскинутых на несколько файлов.
'''



'''/unban'''
# appellant — подающий апелляцию, admin — принимающий.
appealData = {}   # Хранит в себе данные об апелляции (см. AppealDataclass).
messagesData = {} # Хранит в себе данные о сообщениях, написаные апеллянтом.

class FSMunban(StatesGroup):
    text = State() # Сообщение апеллянта. Значение сливается в `messageData[appellant_id][f'message_{messageCount}']`, а после обнуляется.
    time = State() # Установка времени таймаута админом (unbanCbAppealTimeout).

@dataclass
class AppealDataclass:
    appellant_id: int
    appellant_user: str = ""
    admin_id: int = 0
    admin_user: str = ""
    appeal_id: str = ""
    appeal_isAccepted: bool = False # Принята ли апелляция;
    appeal_status: bool = True      # Существует ли апелляция.
    toAdmin_message_id: int = 0
    appellant_message_count: int = 0


async def unbanAppealStatusCheck(appellant_id: int) -> bool:
    '''
    Проверка статуса апелляции.
    Возвращает True если открыта и False если закрыта (и заодно очищает память если апелляция вообще не существует, но есть в памяти).
    '''
    global appealData
    global messagesData
    
    if appellant_id not in appealData:
        return False
    
    appeal_status = appealData[appellant_id].appeal_status
    
    if not appeal_status:
        del appealData[appellant_id]
        del messagesData[appellant_id]
        return False
    
    return True

async def unbanWriteAppealIdInDB(appellant_id: int, state: FSMContext) -> None: # 
    ''' Запись ID апелляции в БД. '''
    global appealData
    appellant_data = await readUser(appellant_id)
    appeal_id = appealData[appellant_id].appeal_id

    if appellant_data[1] == "None":
        appeal_id_for_database = f"{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)
    else:
        appeal_id_for_database = f"{appellant_data[1]}{appeal_id}, "
        await updateUser(appellant_id, appeal_ids=appeal_id_for_database)

    appealData[appellant_id].appeal_status = False
    try: await state.clear()
    except: pass
    await unbanAppealStatusCheck(appellant_id)

async def unbanNoMessageTimeout(appellant_id: int, state: FSMContext) -> None:
    '''Если в течение 24 часов апелляция не была решена, то она закрывается.'''
    global appealData
    global messagesData

    await sleep(86400) # 86к сек. = 24 часа. При изменении - обратить внимание на 108 и 117 строки.

    if appellant_id not in appealData:
        return
    
    if not appealData[appellant_id].appeal_status:
        return

    if appealData[appellant_id].appeal_isAccepted:
        return
    
    appellant_user = appealData[appellant_id].appellant_user

    try:
        if appealData[appellant_id].admin_id != 0:
            await bot.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Истёкшая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id][f'message_{appealData[appellant_id].appellant_message_count}']}</blockquote>\n\n"
                     f"Принял {appealData[appellant_id].admin_user}\n"
                     f"Прошло 24 часа, но решение так и не было вынесено.",
                    reply_markup=None
            )
        else:
            await bot.edit_message_text(
                chat_id=ID_OERCHAT_ADMIN,
                message_id=appealData[appellant_id].toAdmin_message_id,
                text=f"🆘 <b>Истёкшая апелляция</b> — {appellant_user}\n"
                     f"<blockquote>{messagesData[appellant_id]['message_1']}</blockquote>\n\n"
                     f"Прошло 24 часа, но жалоба так и не была решена.",
                    reply_markup=None
            )

        await bot.send_message(
            chat_id=appellant_id,
            text=("⏰ <b>Ваша жалоба была автоматически закрыта.</b> Прошли сутки, а она не продвинулась.")
        )

    except TelegramBadRequest as e:
        print(f"(X) oerChat/adminside.py: unbanNoMessageTimeout(): TelegramBadRequest — {e}.") if logErrorsBool else None
    except Exception as e:
        print(f"(XX) oerChat/adminside.py: unbanNoMessageTimeout(): {e}.")

    try: await state.clear()
    except: pass
    await unbanWriteAppealIdInDB(appellant_id, state)