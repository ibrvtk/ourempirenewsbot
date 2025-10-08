# import aiosqlite

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



def unbanKeyboard_(user_id: int):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="✅ Принять", callback_data=f"unbanAppealAccept_{user_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"unbanAppealDecline_{user_id}"))
    keyboard.add(InlineKeyboardButton(text="⏱️ Тайм-аут", callback_data=f"unbanAppealTimeOut_{user_id}"))
    
    return keyboard.adjust(3).as_markup()

def unbanKeyboardAcceptedActions_(user_id: int):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text="✅ Разбан", callback_data=f"unbanUnbanAccept_{user_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отказ", callback_data=f"unbanUnbanDecline_{user_id}"))
    
    return keyboard.adjust(2).as_markup()