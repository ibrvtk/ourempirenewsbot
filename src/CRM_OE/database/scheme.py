from config import (
    DB_CRM_PATH,
    LOG_ERRORS, LOG_OTHERS
)

from aiosqlite import connect



# C
async def createTable() -> None:
    try:
        async with connect(DB_CRM_PATH) as db:
            with open('src/CRM_OE/database/scheme.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: createTable(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: createTable(): {e}.")


async def createUser(user_id: int) -> None:
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                INSERT OR IGNORE INTO players 
                (user_id, adminLevel, reputation, countryName, countryFlag, countryStatus, points, turnText, turnMediafiles, turnIsSended)
                VALUES (?, 0, 0, 'None', '🏴', 0, 0, 'None', 'None', 0)
            """, (user_id,))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: createUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: createUser(): {e}.")


# R
async def readUser(user_id: int):
    try:
        async with connect(DB_CRM_PATH) as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
                print("(V) CRM_OE/database/scheme.py: readUser(): Успех.") if LOG_OTHERS else None
                return user_data
    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: readUser(): {e}.")
        return None
    
async def readUsers():
    try:
        async with connect(DB_CRM_PATH) as db:
            async with db.execute("SELECT user_id, countryName, countryFlag, countryStatus, adminLevel FROM players") as cursor:
                users_data = await cursor.fetchall()
                print("(V) CRM_OE/database/scheme.py: readUsers(): Успех.") if LOG_OTHERS else None
                return users_data
    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: readUsers(): {e}.")
        return []


# U
async def updateUserFull(user_id: int, adminLevel: int = 0, reputation: int = 0,
                     countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0, points: int = 0,
                     turnText: str = "None", turnMediafiles: str = "None", turnIsSended: int = 0):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET adminLevel = ?, reputation = ?, countryName = ?, countryFlag = ?, 
                    countryStatus = ?, points = ?, turnText = ?, turnMediafiles = ?, turnIsSended = ?
                WHERE user_id = ?
            """, (adminLevel, reputation, countryName, countryFlag, countryStatus, points, 
                  turnText, turnMediafiles, turnIsSended, user_id))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: updateUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateUser(): {e}.")

async def updateUser5(user_id: int, adminLevel: int = 0, reputation: int = 0,
                     countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0, points: int = 0):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET adminLevel = ?, reputation = ?, countryName = ?, countryFlag = ?, 
                    countryStatus = ?, points = ?
                WHERE user_id = ?
            """, (adminLevel, reputation, countryName, countryFlag, countryStatus, points, user_id))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: updateUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateUser(): {e}.")
    
async def updateUser2(user_id: int, countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET countryName = ?, countryFlag = ?, 
                    countryStatus = ?
                WHERE user_id = ?
            """, (countryName, countryFlag, countryStatus, user_id))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: updateUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateUser(): {e}.")

async def updateReputation(user_id: int, reputation: int):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET reputation = ?
                WHERE user_id = ?
            """, (reputation, user_id))
            await db.commit()

            print("(V) CRM_OE/database/scheme.py: updateReputation(): Успех.") if LOG_OTHERS else None
            return True

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateReputation(): {e}.")
        return False
    
async def updatePoints(user_id: int, points: int):
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET points = ?
                WHERE user_id = ?
            """, (points, user_id))
            await db.commit()

            print("(V) CRM_OE/database/scheme.py: updateReputation(): Успех.") if LOG_OTHERS else None
            return True

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: updateReputation(): {e}.")
        return False


# D
async def deleteUser(user_id: int) -> None:
    try:
        async with connect(DB_CRM_PATH) as db:
            await db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            await db.commit()
            print("(V) CRM_OE/database/scheme.py: deleteUser(): Успех.") if LOG_OTHERS else None

    except Exception as e:
        print(f"(XX) CRM_OE/database/scheme.py: deleteUser(): {e}.")