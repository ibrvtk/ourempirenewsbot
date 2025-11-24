from config import (
    DB_CRM_SCHEME_PATH, DB_CRM_PLAYERS_PATH,
    logDatabasesBool
)
from master.logging import logError, logOther

from aiosqlite import connect



# C
async def createTable() -> None:
    '''Создание таблицы players БД ЦРМ.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            with open(DB_CRM_SCHEME_PATH, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()
            await logOther("(V) crm/database/scheme.py: createTable(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: createTable(): {e}.", True)
        return


async def createUser(user_id: int) -> None:
    '''Добавление человека в таблицу, используя параметры по умолчанию.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                INSERT OR IGNORE INTO players 
                (user_id, adminLevel, reputation, countryName, countryFlag, countryStatus, points, turnText, turnMediafiles, turnIsSended)
                VALUES (?, 0, 0, 'None', '🏴', 0, 0, 'None', 'None', 0)
            """, (user_id,))
            await db.commit()
            await logOther("(V) crm_darabase/scheme.py: createUser(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: createUser(): {e}.", True)
        return

# R
async def readUser(user_id: int):
    '''
    Чтение всех данных человека.
    Возвращает список всех данных.
    '''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                user_data = await cursor.fetchone()
                await logOther("(V) crm/database/scheme.py: readUser(): Успех.") if logDatabasesBool else None
                return user_data

    except Exception as e:
        await logError(f"crm/database/scheme.py: readUser(): {e}.", True)
        return None
    
async def readUsers():
    '''
    Чтение данных всех людей, что есть в таблице.
    Возвращает только TG-ID, название и флаг страны, статус капитуляции и уровень админки.
    '''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            async with db.execute("SELECT user_id, countryName, countryFlag, countryStatus, adminLevel FROM players") as cursor:
                users_data = await cursor.fetchall()
                await logOther("(V) CRM_OE/database/scheme.py: readUsers(): Успех.") if logDatabasesBool else None
                return users_data

    except Exception as e:
        await logError(f"crm/database/scheme.py: readUsers(): {e}.", True)
        return None


# U
async def updateUserFull(user_id: int, adminLevel: int = 0, reputation: int = 0,
                     countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0, points: int = 0,
                     turnText: str = "None", turnMediafiles: str = "None", turnIsSended: int = 0) -> None:
    '''Обновление всех параметров пользователя.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET adminLevel = ?, reputation = ?, countryName = ?, countryFlag = ?, countryStatus = ?, points = ?, turnText = ?, turnMediafiles = ?, turnIsSended = ?
                WHERE user_id = ?
            """, (adminLevel, reputation, countryName, countryFlag, countryStatus, points, 
                  turnText, turnMediafiles, turnIsSended, user_id))
            await db.commit()
            await logOther("(V) crm/database/scheme.py: updateUserFull(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: updateUserFull(): {e}.", True)
        return

async def updateUser5(user_id: int, adminLevel: int = 0, reputation: int = 0,
                     countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0, points: int = 0) -> None:
    '''Обновление всех параметров пользователя, кроме текста и медиафайлов хода и его статус отправки.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET adminLevel = ?, reputation = ?, countryName = ?, countryFlag = ?, countryStatus = ?, points = ?
                WHERE user_id = ?
            """, (adminLevel, reputation, countryName, countryFlag, countryStatus, points, user_id))
            await db.commit()
            await logOther("(V) crm/database/scheme.py: updateUser5(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: updateUser5(): {e}.", True)
        return
    
async def updateUser2(user_id: int, countryName: str = "None", countryFlag: str = "🏴", countryStatus: int = 0) -> None:
    '''Обновление параметров пользователя название, флаг и статус капитуляции.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET countryName = ?, countryFlag = ?, countryStatus = ?
                WHERE user_id = ?
            """, (countryName, countryFlag, countryStatus, user_id))
            await db.commit()
            await logOther("(V) crm/database/scheme.py: updateUser2(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: updateUser2(): {e}.", True)
        return

async def updateReputation(user_id: int, reputation: int) -> None:
    '''Обновление параметра репутации человека.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET reputation = ?
                WHERE user_id = ?
            """, (reputation, user_id))
            await db.commit()
            logOther("(V) crm/database/scheme.py: updateReputation(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: updateReputation(): {e}.", True)
        return
    
async def updatePoints(user_id: int, points: int) -> None:
    '''Обновление параметров очков влияния у человека.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("""
                UPDATE players 
                SET points = ?
                WHERE user_id = ?
            """, (points, user_id))
            await db.commit()
            await logOther("(V) crm/database/scheme.py: updatePoints(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: updatePoints(): {e}.", True)
        return


# D
async def deleteUser(user_id: int) -> None:
    '''Удаление человека из таблицы.'''
    try:
        async with connect(DB_CRM_PLAYERS_PATH) as db:
            await db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            await db.commit()
            await logOther("(V) crm/database/scheme.py: deleteUser(): Успех.") if logDatabasesBool else None

    except Exception as e:
        await logError(f"crm/database/scheme.py: deleteUser(): {e}.", True)
        return