from config import DB_PLAYERS_PATH

import aiosqlite
import os



async def createTable():
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            with open('scheme.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
        print("(V) scheme.py: createTable(): успех.")

    except Exception as e:
        print(f"(XXX) scheme.py: createTable(): {e}.")


async def createUser(user_id: int, points: int = 0, adminLevel: int = 0,
              country: str = "None", eventsType: int = 0,
              moveText: str = "None", moveMediafiles: str = "None", moveIsSended: int = 0):
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO players (user_id, points, adminLevel, country, eventsType, moveText, moveMediafiles, moveIsSended)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, points, adminLevel, country, eventsType, moveText, moveMediafiles, moveIsSended))
            await db.commit()
            print("(V) scheme.py: createUser(): успех.")
            return cursor.lastrowid

    except Exception as e:
        print(f"(XX) scheme.py: createUser(): {e}.")


async def readUser(user_id: int):
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
                print("(V) scheme.py: readUser(): успех.")
                return user_data
    except Exception as e:
        print(f"(XX) scheme.py: readUser(): {e}")
        return None
    
async def readUsers():
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            async with db.execute("SELECT * FROM players") as cursor:
                users = await cursor.fetchall()
                print("(V) scheme.py: readUsers(): успех.")
                return users
    except Exception as e:
        print(f"(XX) scheme.py: readUsers(): {e}")
        return []
    

async def updateUser(user_id: int, **kwargs):
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            setClause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(user_id)
            
            await db.execute(f"UPDATE players SET {setClause} WHERE user_id = ?", values)
            await db.commit()
            print("(V) scheme.py: updateUser(): успех.")

    except Exception as e:
        print(f"(XX) scheme.py: updateUser(): {e}")
    

async def deleteUser(user_id: int):
    try:
        async with aiosqlite.connect(DB_PLAYERS_PATH) as db:
            await db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            await db.commit()
            print("(V) scheme.py: deleteUser(): успех.")

    except Exception as e:
        print(f"(XX) scheme.py: deleteUser(): {e}")