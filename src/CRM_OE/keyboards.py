# import aiosqlite

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



adminpanelKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Изменить права", callback_data="adminpanelEditRights"),
     InlineKeyboardButton(text="📜 Список всех игроков", callback_data="adminpanelGetPlayers")] # from scheme import getUsers(), if result[3] != "None"
])