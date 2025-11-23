from config import (
    bot
)
from master.logging import logError, logOther

from oer.database.appeals import updateUser, getTimeouts

from asyncio import sleep



async def schedulerAppealsTimeout():
    while True:
        try:
            due_timeouts = await getTimeouts()
            
            for timeout in due_timeouts:
                appellant_id = timeout['appellant_id']
                
                await updateUser(appellant_id, timeout=0)
                
                await bot.send_message(
                    chat_id=appellant_id,
                    text="📳 <b>Таймаут окончен!</b>"
                )
                
                await logOther(f"(V) oer/database/scheduler.py: Таймаут для {appellant_id} сброшен.")
                
        except Exception as e:
            if "database is locked" in str(e):
                await logError("oer/database/appeals.py: schedulerAppealsTimeout(): База данных недоступна.", True)
            else:
                await logError(f"oer/database/appeals.py: schedulerAppealsTimeout(): {e}.", True)
        
        await sleep(30)  # 30 секунд.