# Сторонние библиотеки _(.venv)_

* aiogram 3.22.0
* aiosqlite 0.21.0
* python-dotenv 1.1.1

# Файл .env

```
TOKEN=<token>
SUPERADMIN=<id>


DB_OER_USERS_PATH=src/oerChat/databases/users.db
DB_OER_APPEALS_PATH=src/oerChat/databases/appeals.db

DB_CRM_PLAYERS_PATH=src/CRM_OE/database/players.db


ID_OERCHAT=-100<id>
ID_OERCHAT_ADMIN=-100<id>
ID_OERCHAT_ADMIN_APPEALS_THREAD=<message_thread_id>

ID_CRM_OE=-100<id>
ID_CRM_OE_ADMIN=-100<id>
```

# Коды чатов

* `oer*` — oerChat
* `crm*` — CRM_OE

# Дополнительная информация

* Python 3.12.3
* Гитхаб репозиторий "перекочевал" из `vkuskiy/oerChatBot` _(Нишка)_ _(ныне удалено)_ на `ibrvtk/ourempirenewsbot`.
* `Type checking` должен быть `off`, что бы избежать "критические" ошибки «Отсутствует проверка на None».
* `(i)` - информационное уведомление, `(+)` - создан новый процесс.
* `(V)` - успешная операция, `(X)` - ошибка, `(XX)` - непредвиденная ошибка.
* `*/userside.py` - публичные команды, `*/adminside.py` - команды только для админов.
* В названиях функций: `cmd` - команда, `cb` - коллбэк, `text` - `F.text`, `uni` - смешанное.

## Написано с помощью ИИ

* `oerChat/adminside.py`: `cmdUnban()`: `if appellant_data and appellant_data[2] > datetime.now().timestamp():` — [**DeepSeek**](https://www.deepseek.com)
* `oerChat/databases/appeals.py`: `getTimeouts()` — [**DeepSeek**](https://www.deepseek.com)
* `oerChat/databases/scheduler.py` — [**DeepSeek**](https://www.deepseek.com)
* `CRM_OE/database/scheme.py`: `readUsers()`, `updateUser()` — [**DeepSeek**](https://www.deepseek.com)
* `CRM_OE/adminside.py`: `fsmAdminpanelEditRightsText()` — [**DeepSeek**](https://www.deepseek.com)
* `config.py`: `delayMsgDelete()` — [**DeepSeek**](https://www.deepseek.com)