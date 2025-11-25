from config import (
    logErrorsBool, logOthersBool
)

from datetime import datetime



async def logError(message, forced: bool = False) -> None:
    '''
    **Логгирование ошибки.**
    `message` — сообщение, которое будет выведено в терминал.
    `forced` — логгировать принудительно?
    '''
    if not logErrorsBool:
        if not forced:
            return
    
    timestamp = datetime.now().strftime("%H:%M")
    print(f"[{timestamp}] (X) {message}")

async def logOther(message):
    '''
    **Логгирование любой информации.**
    `message` — сообщение, которое будет выведено в терминал.
    '''
    if not logOthersBool:
        return
    
    timestamp = datetime.now().strftime("%H:%M")
    print(f"[{timestamp}] {message}")