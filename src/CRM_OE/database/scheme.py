from config import logErrors, DB_CRM_PATH

from aiosqlite import connect



async def createTable():                
    try:
        async with connect(DB_CRM_PATH) as db:
            with open('src/CRM_OE/database/scheme.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
        print("(V) CRM_OE/database/scheme.py: createTable(): успех.") if logErrors else None

    except Exception as e:
        print(f"(XXX) CRM_OE/database/scheme.py: createTable(): {e}.")


async def createUser(user_id: int, points: int = 0, adminLevel: int = 0,
              country: str = "None", eventsType: int = 0,
              moveText: str = "None", moveMediafiles: str = "None", moveIsSended: int = 0):
    try:
        async with connect(DB_CRM_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO players (user_id, points, adminLevel, country, eventsType, moveText, moveMediafiles, moveIsSended)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, points, adminLevel, country, eventsType, moveText, moveMediafiles, moveIsSended))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: createUser(): успех.") if logErrors else None
            return cursor.lastrowid

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: createUser(): {e}.")


async def readUser(user_id: int):
    try:
        async with connect(DB_CRM_PATH) as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
                print("(V) CRM_OE/database/scheme.py: readUser(): успех.") if logErrors else None
                return user_data
    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: readUser(): {e}.")
        return None
    
async def readUsers():
    try:
        async with connect(DB_CRM_PATH) as db:
            async with db.execute("SELECT * FROM players") as cursor:
                users = await cursor.fetchall()
                print("(V) CRM_OE/database/scheme.py: readUsers(): успех.") if logErrors else None
                return users
    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: readUsers(): {e}.")
        return []
    

async def updateUser(user_id: int, **kwargs):
    try:
        async with connect(DB_CRM_PATH) as db:
            setClause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(user_id)
            
            await db.execute(f"UPDATE players SET {setClause} WHERE user_id = ?", values)
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: updateUser(): успех.") if logErrors else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateUser(): {e}.")
    

async def deleteUser(user_id: int):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: deleteUser(): успех.") if logErrors else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: deleteUser(): {e}.")