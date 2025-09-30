CREATE TABLE IF NOT EXISTS "players" (
    "user_id" INTEGER PRIMARY KEY,
    "points" INTEGER DEFAULT 0,
    "adminLevel" INTEGER DEFAULT 0,
    "country" TEXT DEFAULT "None",
    "eventsType" INTEGER DEFAULT 0,
    "moveText" TEXT DEFAULT "None",
    "moveMediafiles" TEXT DEFAULT "None",
    "moveIsSended" INTEGER DEFAULT 0
);