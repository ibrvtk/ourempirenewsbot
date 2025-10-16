# import aiosqlite

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



def unbanKeyboard_(appeal_id: str):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="✅ Принять", callback_data=f"unbanAppealAccept_{appeal_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"unbanAppealDecline_{appeal_id}"))
    keyboard.add(InlineKeyboardButton(text="⏱️ Тайм-аут", callback_data=f"unbanAppealTimeout_{appeal_id}"))
    
    return keyboard.adjust(3).as_markup()

def unbanKeyboardAcceptedActions_(appeal_id: str):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="✅ Разбан", callback_data=f"unbanAppealAcceptUnban_{appeal_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отказ", callback_data=f"unbanAppealDeclineUnban_{appeal_id}"))
    keyboard.add(InlineKeyboardButton(text="◀️", callback_data=f"unbanAppealHistoryPrev_{appeal_id}"))
    keyboard.add(InlineKeyboardButton(text="▶️", callback_data=f"unbanAppealHistoryNext_{appeal_id}"))
    
    return keyboard.adjust(2).as_markup()