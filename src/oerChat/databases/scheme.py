from config import logOther, DB_OER_APPEALS_PATH

from aiosqlite import connect



async def createTable() -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            with open('src/oerChat/databases/scheme.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
        print("(V) oerChat/databases/scheme.py: createTable(): успех.") if logOther else None

    except Exception as e:
        print(f"(XXX) oerChat/databases/scheme.py: createTable(): {e}.")