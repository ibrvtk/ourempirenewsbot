from config import BOT
from oerChat.databases.appeals import updateUser, getTimeouts

from asyncio import sleep

async def schedulerAppealsTimeout():
    while True:
        try:
            due_timeouts = await getTimeouts()
            
            for timeout in due_timeouts:
                appellant_id = timeout['appellant_id']
                
                # Сбрасываем таймаут
                await updateUser(appellant_id, timeout=0)
                
                # Уведомляем пользователя
                await BOT.send_message(
                    chat_id=appellant_id,
                    text="📳 <b>Таймаут окончен!</b>"
                )
                
                print(f"(V) Таймаут для {appellant_id} сброшен.")
                
        except Exception as e:
            print(f"(XX) oerChat/databases/scheduler.py: {e}.")
        
        await sleep(30)  # Проверяем каждые 30 секунд