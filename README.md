# Телеграм-бот для ру сообщества Our Empire

## Функционал

### [@oerChat](https://t.me/oerChat)

* Подача апелляций забанеными в [сетке](https://blog.ourempire.ru/chats) и их рассмотрение модерацией.

### [@CRM_OE](https://t.me/CRM_OE)

* Удаление //оффтопа.
* Добавление игроков в соответствующую БД _(W.I.P.)_. Команда `/who` для идентефикации.

## Дополнительная информация

* [Python 3.12.3](https://www.python.org/downloads/release/python-3123)
* W.I.P. 0.3.4
* Гитхаб репозиторий "перекочевал" из `vkuskiy/oerChatBot` _(Нишка)_ _(ныне удалено)_ на `ibrvtk/ourempirenewsbot`.
* `Type checking` должен быть `off`, что бы избежать "критические" ошибки «Отсутствует проверка на None».
* Типы уведомлений в терминале:
  * `(i)` - информационное уведомление, `(+)` - создан новый процесс;
  * `(V)` - успешная операция, `(X)` - ошибка, `(XX)` - непредвиденная ошибка.
* `*/userside.py` - публичные команды, `*/adminside.py` - команды только для админов.
* В названиях функций: `cmd` - команда, `cb` - коллбэк, `text` - `F.text`, `uni` - смешанное.
  * Eсли "уникод фукнции" стоит в конце _(например `unbanCmd()`)_ - команда вызывает цепочку действий. Иначе _(например `cmdCancel()`)_ на один раз.

### Коды чатов

* `oer*` — [@oerChat](https://t.me/oerChat)
* `crm*` — [@CRM_OE](https://t.me/CRM_OE)

### Написано с помощью ИИ

* [`oerChat/databases/appeals.py`](src/oerChat/databases/appeals.py): `getTimeouts()` — [**DeepSeek**](https://www.deepseek.com)
* [`oerChat/databases/scheduler.py`](src/oerChat/databases/scheduler.py) — [**DeepSeek**](https://www.deepseek.com)
* [`CRM_OE/database/scheme.py`](src/CRM_OE/database/scheme.py): `readUsers()`, `updateUser()` — [**DeepSeek**](https://www.deepseek.com)

## Файл .env

```
TOKEN=<token>                              # Токен бота.
SUPERADMIN=<*user.id>                      # Суперадмин обладает сверхправами и может управлять ботом, даже будучи не записаным в какую-либо БД.
SUPERADMIN_ARRAY=<*user.id>,<*user.id>,... # Список суперадминов (если понадобится несколько).


DB_OER_USERS_PATH=src/oerChat/databases/users.db     # Пусть к oer-БД с данными об активных пользователях.
DB_OER_APPEALS_PATH=src/oerChat/databases/appeals.db # Пусть к oer-БД с данными об апелляциях и таймаутах.

DB_CRM_PLAYERS_PATH=src/CRM_OE/database/players.db # Пусть к oer-БД с данными об игроках.


ID_OERCHAT=-100<chat_id>
ID_OERCHAT_ADMIN=-100<chat_id>
ID_OERCHAT_ADMIN_APPEALS_THREAD=<message_thread_id>

ID_CRM_OE=-100<chat_id>
ID_CRM_OE_ADMIN=-100<chat_id>
```