# Используемые библиотеки _(.venv)_

* aiogram <u>3.22.0</u>
* aiosqlite <u>0.21.0</u>
* python-dotenv <u>1.1.1</u>

# Файл .env

```
TOKEN=<token>



SUPERADMIN=<id>


DB_ORC_USERS_PATH=src/oerChat/databases/users.db
DB_ORC_USERS_PATH=src/oerChat/databases/appeals.db

DB_CRM_PLAYERS_PATH=src/CRM_OE/database/players.db


ID_OERCHAT=-100<id>
ID_OERCHAT_ADMIN=-100<id>

ID_CRM_OE=-100<id>
ID_CRM_OE_ADMIN=-100<id>
```

# Коды чатов

* `oer*` — oerChat
* `crm*` — CRM_OE

# Дополнительная информация

* Гитхаб репозиторий "перекочевал" из `vkuskiy/oerChatBot` _(ныне удалено)_ на `ibrvtk/ourempirenewsbot`.
* `Type checking` должен быть `off`, что бы избежать "критические" ошибки «Отсутствует проверка на None».
* `(V)` - успешная операция, `(X)` - ошибка, `(XX)` - непредвиденная ошибка, `(XXX)` - критическая ошибка. Названия ошибок в этом файле не обязательно относятся к их **чисто** техническим последствиям.
* `*/userside.py` - публичные команды, `*/adminside.py` - команды только для админов.
* В названиях функций: `cmd` - команда, `cb` - колбэк, `text` - `F.text`, `uni` - смешанное.

## Написано с помощью ИИ

* `CRM_OE/database/scheme.py`: `readUsers()`, `updateUser()` — [**DeepSeek**](https://www.deepseek.com)
* `CRM_OE/app/adminside.py`: `fsmAdminpanelEditRightsText()` — [**DeepSeek**](https://www.deepseek.com)
* `config.py`: `delayMsgDelete()` — [**DeepSeek**](https://www.deepseek.com)