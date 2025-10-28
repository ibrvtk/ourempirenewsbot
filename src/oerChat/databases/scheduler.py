from config import (
    BOT,
    LOG_OTHERS
)

from oerChat.databases.appeals import updateUser, getTimeouts

from asyncio import sleep



async def schedulerAppealsTimeout():
    while True:
        try:
            due_timeouts = await getTimeouts()
            
            for timeout in due_timeouts:
                appellant_id = timeout['appellant_id']
                
                await updateUser(appellant_id, timeout=0)
                
                await BOT.send_message(
                    chat_id=appellant_id,
                    text="📳 <b>Таймаут окончен!</b>"
                )
                
                print(f"(V) oerChat/databases/scheduler.py: Таймаут для {appellant_id} сброшен.") if LOG_OTHERS else None
                
        except Exception as e:
            print(f"(XX) oerChat/databases/scheduler.py: {e}.")
        
        await sleep(30)  # 30 секунд.