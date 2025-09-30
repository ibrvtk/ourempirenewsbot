# Используемые библиотеки _(.venv)_

* aiogram <u>3.22.0</u>
* aiosqlite <u>0.21.0</u>
* python-dotenv <u>1.1.1</u>

# Файл .env

```
TOKEN=
DB_PLAYERS_PATH=

ID_OERCHAT=-100
ID_CRM_OE=-100
```

# Коды чатов

* `orc*` — oerChat
* `crm*` — CRM_OE

# Дополнительная информация

* Гитхаб репозиторий "перекочевал" из `vkuskiy/oerChatBot` _(ныне удалено)_ на `ibrvtk/ourempirenewsbot`.
* `Type checking` должен быть `off`, что бы избежать "критические" ошибки «Отсутствует проверка на None».
* `(V)` - успешная операция, `(X)` - ошибка, `(XX)` - непредвиденная ошибка, `(XXX)` - критическая ошибка.

## Написано с помощью ИИ
* `src/CRM_OE/database/scheme.py`: `readUsers()`, `updateUser()` — [DeepSeek](https://www.deepseek.com)