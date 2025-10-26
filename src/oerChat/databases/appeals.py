from config import LOG_OTHERS, LOG_ERRORS, DB_OER_APPEALS_PATH

from aiosqlite import connect, Row
from datetime import datetime



async def createUser(appellant_id: int, appeal_ids: str = "None", timeout: int = 0):
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            cursor = await db.execute("""
                INSERT OR IGNORE INTO appeals (appellant_id, appeal_ids, timeout)
                VALUES (?, ?, ?)
            """, (appellant_id, appeal_ids, timeout))
            await db.commit()
            changes = cursor.rowcount
        
            if changes > 0:
                print("(V) oerChat/databases/appeals.py: createUser(): Успех.") if LOG_OTHERS else None
                return cursor.lastrowid
            else:
                print(f"(i) oerChat/databases/appeals.py: createUser(): @{appellant_id} уже существует.") if LOG_ERRORS or LOG_OTHERS else None
                return None

    except Exception as e:
        print(f"(XX) oerChat/databases/appeals.py: createUser(): {e}.")


async def readUser(appellant_id: int):
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            async with db.execute("SELECT * FROM appeals WHERE appellant_id = ?", (appellant_id,)) as cursor:
                user_data = await cursor.fetchone()
                print("(V) oerChat/databases/appeals.py: readUser(): Успех.") if LOG_OTHERS else None
                return user_data
            
    except Exception as e:
        print(f"(XX) oerChat/databases/appeals.py: readUser(): {e}.")
        return None
    

async def updateUser(appellant_id: int, **kwargs) -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            setClause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(appellant_id)
            
            await db.execute(f"UPDATE appeals SET {setClause} WHERE appellant_id = ?", values)
            await db.commit()
            print("(V) oerChat/databases/appeals.py: updateUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) oerChat/databases/appeals.py: updateUser(): {e}.")
    

async def deleteUser(appellant_id: int) -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            await db.execute("DELETE FROM appeals WHERE appellant_id = ?", (appellant_id,))
            await db.commit()
            print("(V) oerChat/databases/appeals.py: deleteUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) oerChat/databases/appeals.py: deleteUser(): {e}.")


async def getTimeouts():
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            db.row_factory = Row
            async with db.execute(
                "SELECT appellant_id FROM appeals WHERE timeout > 0 AND timeout <= ?", 
                (int(datetime.now().timestamp()),)
            ) as cursor:
                return await cursor.fetchall()
            
    except Exception as e:
        print(f"(XX) oerChat/databases/appeals.py: get_due_timeouts(): {e}.")
        return []