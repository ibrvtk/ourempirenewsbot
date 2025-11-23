from config import (
    logDatabasesBool,
    DB_OER_SCHEME_PATH, DB_OER_APPEALS_PATH
)
from master.logging import logError, logOther

from aiosqlite import connect



# async def createTableUsers() -> None:
#     try:
#         async with connect(DB_OER_USERS_PATH) as db:
#             with open('src/oerChat/databases/scheme.sql', 'r', encoding='utf-8') as file:
#                 sql_script = file.read()
#             await db.executescript(sql_script)
#             await db.commit()
#         print("(V) oerChat/databases/scheme.py: createTableUsers(): успех.") if logOther else None

#     except Exception as e:
#         print(f"(XXX) oerChat/databases/scheme.py: createTableUsers(): {e}.")


async def createTableAppeals() -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            with open(DB_OER_SCHEME_PATH, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
        await logOther("(V) oer/database/scheme.py: createTableAppeals(): успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"oer/database/scheme.py: createTableAppeals(): {e}.", True)