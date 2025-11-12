from config import (
    logDatabasesBool,
    DB_OER_APPEALS_PATH
)
from master.logging import logError, logOther

from datetime import datetime
from aiosqlite import connect, Row



async def createUser(appellant_id: int, appeal_ids: str = "None", timeout: int = 0) -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            cursor = await db.execute("""
                INSERT OR IGNORE INTO appeals (appellant_id, appeal_ids, timeout)
                VALUES (?, ?, ?)
            """, (appellant_id, appeal_ids, timeout))
            await db.commit()
            changes = cursor.rowcount
        
            if changes > 0:
                await logOther("(V) oer/database/appeals.py: createUser(): Успех.") if logDatabasesBool else None
                return cursor.lastrowid
            else:
                await logOther(f"(i) oer/database/appeals.py: createUser(): @{appellant_id} уже существует.") if logDatabasesBool else None
                return None

    except Exception as e:
        if "database is locked" in str(e):
            await logError("oer/database/appeals.py: createUser(): База данных недоступна.", True)
        else:
            await logError(f"oer/database/appeals.py: createUser(): {e}.", True)


async def readUser(appellant_id: int):
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            async with db.execute("SELECT * FROM appeals WHERE appellant_id = ?", (appellant_id,)) as cursor:
                user_data = await cursor.fetchone()
                await logOther("(V) oer/database/appeals.py: readUser(): Успех.") if logDatabasesBool else None
                return user_data
            
    except Exception as e:
        if "database is locked" in str(e):
            await logError("oer/database/appeals.py: readUser(): База данных недоступна.", True)
        else:
            await logError(f"oer/database/appeals.py: readUser(): {e}.", True)
        return None
    

async def updateUser(appellant_id: int, **kwargs) -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            setClause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(appellant_id)
            
            await db.execute(f"UPDATE appeals SET {setClause} WHERE appellant_id = ?", values)
            await db.commit()
            logOther("(V) oer/database/appeals.py: updateUser(): Успех.") if logDatabasesBool else None

    except Exception as e:
        if "database is locked" in str(e):
            await logError("oer/database/appeals.py: updateUser(): База данных недоступна.", True)
        else:
            await logError(f"oer/database/appeals.py: updateUser(): {e}.", True)
    

async def deleteUser(appellant_id: int) -> None:
    try:
        async with connect(DB_OER_APPEALS_PATH) as db:
            await db.execute("DELETE FROM appeals WHERE appellant_id = ?", (appellant_id,))
            await db.commit()
            print("(V) oer/database/appeals.py: deleteUser(): Успех.") if logDatabasesBool else None

    except Exception as e:
        if "database is locked" in str(e):
            await logError("oer/database/appeals.py: deleteUser(): База данных недоступна.", True)
        else:
            await logError(f"oer/database/appeals.py: deleteUser(): {e}.", True)


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
        if "database is locked" in str(e):
            await logError("oer/database/appeals.py: getTimeouts(): База данных недоступна.", True)
        else:
            await logError(f"oer/database/appeals.py: getTimeouts(): {e}.", True)
        return []