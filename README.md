# Телеграм-бот для ру сообщества Our Empire

## Функционал

### [@oerChat](https://t.me/oerChat)

* Подача апелляций забанеными в [сетке](https://blog.ourempire.ru/chats) командой [`/unban`](src/oer/admin/handlers.py) и их рассмотрение модерацией, с возможность отвечать.

### [@CRM_OE](https://t.me/CRM_OE)

* Удаление //оффтопа из топиков [ID_CRM_OE_NONOFFTOP_THREADS](example.env).
* CRUD взаимодействие с людьми из БД [DB_CRM_PLAYERS_PATH](example.env) с разными правами. Команда [`/who`](src/crm/user/handlers.py) для быстрой идентефикации.
* Автоматическое составление списка стран.
* Удаление сообщений от не игроков в топиках [И] (для игроков).

## О проекте

* [Python 3.12.3](https://www.python.org/downloads/release/python-3123), [aiogram 3.22.0](https://t.me/aiogram_live/125).
* W.I.P. 0.4.4.4
* Гитхаб репозиторий "перекочевал" из `vkuskiy/oerChatBot` _(Нишка)_ _(ныне удалено)_ на `ibrvtk/ourempirenewsbot`.
* `Type checking` должен быть `off`, что бы избежать "критические" ошибки «Отсутствует проверка на None».
* Типы уведомлений в терминале:
  * `(i)` - информационное уведомление, `(+)` - создан новый процесс;
  * `(V)` - успешная операция, `(X)` - ошибка.
* `*/userside.py` - публичные команды, `*/adminside.py` - команды только для админов.
* В названиях функций: `cmd` - команда, `fcmd` - `F.text`, `cb` - коллбэк, `uni` - смешанное.
  * (Eсли "уникод фукнции" стоит в конце _(например [`unbanCmd()`](src/oer/admin/handlers.py))_ - команда вызывает цепочку действий. Иначе _(например [`cmdCancel()`](src/master/handlers.py))_ на один раз)

### Коды чатов

* `*oer*` — [@oerChat](https://t.me/oerChat)
* `*crm*` — [@CRM_OE](https://t.me/CRM_OE)

### Написано с помощью ИИ

* [`master/logging.py`](src/master/logging.py): `timestamp = datetime.now().strftime("%H:%M")` — [**DeepSeek**](https://www.deepseek.com)
* [`oer/admin/handlers.py`](src/oer/admin/handlers.py): `unbanAdminMessage()` — [**DeepSeek**](https://www.deepseek.com)
* [`oer/admin/callbacks.py`](src/oer/admin/callbacks.py): `unbanTimeoutSetTime()` — [**DeepSeek**](https://www.deepseek.com)
* [`oer/database/appeals.py`](src/oer/database/appeals.py): `getTimeouts()` — [**DeepSeek**](https://www.deepseek.com)
* [`oer/database/scheduler.py`](src/oer/database/scheduler.py) — [**DeepSeek**](https://www.deepseek.com)
* [`crm/database/scheme.py`](src/crm/database/scheme.py): `readUsers()` — [**DeepSeek**](https://www.deepseek.com)

---

![avatar](https://github.com/ibrvtk/pictures/blob/main/ourempirenewsbot.png)