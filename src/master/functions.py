from config import (
    LOG_ERRORS, LOG_OTHERS,
    ID_CRM_OE
)

from asyncio import sleep

from aiogram.types import Message



async def delayMessageDelete(message: Message, delay: int) -> None: # Отложенное удаление сообщения.
    await sleep(delay)
    try:
        await message.delete()

        user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"
        placeholderText = f"{message.message_thread_id}: Удалён оффтоп" if message.chat.id == ID_CRM_OE else "Удалено сообщение по отложке"
        if delay < 60: time_display = f"{delay} секунд"
        else: delay_minutes = delay // 60; time_display = f"{delay_minutes} минут"

        print(f"(V) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText} от {user} (прошло {time_display}).") if LOG_OTHERS else None

    except Exception as e:
        user = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name} ({message.from_user.id})"
        placeholderText = f"{message.message_thread_id}: Оффтоп от {user} не был удалён" if message.chat.id == ID_CRM_OE else f"Отложенное удаление сообщения от {user} не произошло"

        if "message can't be deleted" in str(e):
            print(f"(X) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText}: Бот не смог удалить сообщение. У него есть права?") if LOG_ERRORS else None
        elif "message to delete not found" in str(e):
            print(f"(X) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText}: Бот не смог удалить сообщение. Оно уже удалено?") if LOG_ERRORS else None
        else:
            print(f"(XX) @{message.chat.username if message.chat.username else message.chat.id}: {placeholderText}: {e}.")