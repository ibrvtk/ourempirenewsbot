from config import bot, ID_CRM_OE_ADMIN, loggingErrors
from CRM_OE.database.scheme import updateUser

import CRM_OE.app.keyboards as kb

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


adminside = Router()
NONOFFTOPTOPICS = (43950, 43927, 44448) # Заявления, альянсы, мемы
fsmPlaceholderTextRetry = "Попробуйте снова или отмените действие (/cancel)."



@adminside.message(F.chat.id == ID_CRM_OE_ADMIN, Command("adminpanel"))
async def cmdAdminpanel(message: Message):
    await message.reply("📝 <b>Изменить права</b> — изменить права конкретного человека <i>(сделать игроком, админом и любой другой параметр)</i>.\n\n"
                        "📜 <b>Список всех игроков</b> — список всех людей в БД ЦРМ.",
                        reply_markup=kb.adminpanelKeyboard)

class fsmAdminpanelEditRights(StatesGroup):
    text = State()

@adminside.callback_query(F.data == "adminpanelEditRights")
async def cbAdminpanelEditRights(callback: CallbackQuery, state: FSMContext):
    await state.set_state(fsmAdminpanelEditRights.text)
    await callback.message.edit_text("<b>Использование:</b> user_id, поле=значение, поле2=значение2 и так далее.")

@adminside.message(fsmAdminpanelEditRights.text)
async def fsmAdminpanelEditRightsText(message: Message, state: FSMContext):
    await state.clear()
    text = message.text

    try:
        parts = [part.strip() for part in text.split(',')]
        user_id = int(parts[0])
        
        updates = {}
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                updates[key.strip()] = value.strip()
        
        await updateUser(user_id, **updates)

        user = await bot.get_chat(user_id)
        userMention = f"@{user.username}" if user.username else f"{user.id} {user.first_name}"
        await message.reply(f"Человеку <b>{userMention}</b> изменены параметры <i>(<code>{text}</code>)</i>.")
    
    except (ValueError, IndexError) as e:
        await message.reply(f"❌ <b>Ошибка!</b> Использование: user_id, поле=значение, поле2=значение2 и так далее.\n{fsmPlaceholderTextRetry}")
        print(f"(X) CRM_OE/app/adminside.py: fsmAdminpanelEditRightsText(): {e}.") if loggingErrors else None