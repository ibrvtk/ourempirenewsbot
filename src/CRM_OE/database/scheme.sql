CREATE TABLE IF NOT EXISTS "players" (
    "user_id" INTEGER PRIMARY KEY,
    "adminLevel" INTEGER DEFAULT 0,
    "points" INTEGER DEFAULT 0,
    "reputation" INTEGER DEFAULT 0,
    "countryName" TEXT DEFAULT "None",
    "countryFlag" TEXT DEFAULT "🏴",
    "countryStatus" INTEGER DEFAULT 0,
    "turnText" TEXT DEFAULT "None",
    "turnMediafiles" TEXT DEFAULT "None",
    "turnIsSended" INTEGER DEFAULT 0
);