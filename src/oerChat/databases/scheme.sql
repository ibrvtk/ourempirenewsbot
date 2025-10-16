BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" INTEGER PRIMARY KEY,
    "points" INTEGER DEFAULT 0,
    "adminLevel" INTEGER DEFAULT 0,
    "country" TEXT DEFAULT "None",
    "isBoosty" INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "appeals" (
    "appellant_id" INTEGER PRIMARY KEY,
    "appeal_ids" TEXT DEFAULT "None",
    "timeout" INTEGER DEFAULT 0
);
COMMIT;