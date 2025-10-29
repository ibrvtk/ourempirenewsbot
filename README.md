# Телеграм-бот для ру сообщества Our Empire

## Функционал

### [@oerChat](https://t.me/oerChat)

* Подача апелляций забанеными в [сетке](https://blog.ourempire.ru/chats) командой [`/unban`](src/oerChat/adminside.py) и их рассмотрение модерацией, с возможность отвечать.

### [@CRM_OE](https://t.me/CRM_OE)

* Удаление //оффтопа из топиков [ID_CRM_OE_NONOFFTOP_THREADS](example.env).
* CRUD взаимодействие с людьми из БД [DB_CRM_PLAYERS_PATH](example.env). Команда [`/who`](src/CRM_OE/userside.py) для быстрой идентефикации.

## О проекте

* [Python 3.12.3](https://www.python.org/downloads/release/python-3123)
* W.I.P. 0.4.1
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

* [`oerChat/adminside.py`](src/oerChat/adminside.py): `unbanAdminMessage()` — [**DeepSeek**](https://www.deepseek.com)
* [`oerChat/databases/appeals.py`](src/oerChat/databases/appeals.py): `getTimeouts()` — [**DeepSeek**](https://www.deepseek.com)
* [`oerChat/databases/scheduler.py`](src/oerChat/databases/scheduler.py) — [**DeepSeek**](https://www.deepseek.com)
* [`CRM_OE/database/scheme.py`](src/CRM_OE/database/scheme.py): `readUsers()` — [**DeepSeek**](https://www.deepseek.com)