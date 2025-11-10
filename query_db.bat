@echo off
REM Turso Database Query Script for Windows
REM Usage: query_db.bat [command] [options]
REM Examples:
REM   query_db.bat tables              - Show all tables
REM   query_db.bat stats               - Show statistics
REM   query_db.bat listings 20         - Show 20 listings
REM   query_db.bat listing <id>        - Show specific listing
REM   query_db.bat help                - Show help

setlocal enabledelayedexpansion

REM Load environment variables
if exist .env.local (
    for /f "tokens=*" %%a in (.env.local) do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" if not "!line!"=="" (
            set "!line!"
        )
    )
)

if not exist .env.local if exist .env (
    for /f "tokens=*" %%a in (.env) do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" if not "!line!"=="" (
            set "!line!"
        )
    )
)

REM Check if credentials are set
if not defined TURSO_DATABASE_URL (
    echo ERROR: TURSO_DATABASE_URL not found in .env or .env.local
    exit /b 1
)

if not defined TURSO_AUTH_TOKEN (
    echo ERROR: TURSO_AUTH_TOKEN not found in .env or .env.local
    exit /b 1
)

REM Parse command
set "command=%1"
if "!command!"=="" set "command=help"

if /i "!command!"=="tables" (
    echo.
    echo ===== DATABASE TABLES =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.tables
EOF
    goto :eof
)

if /i "!command!"=="schema" (
    echo.
    echo ===== DATABASE SCHEMA =====
    echo.
    echo --- seen_listings TABLE ---
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.schema seen_listings
EOF
    echo.
    echo --- vehicle_details TABLE ---
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.schema vehicle_details
EOF
    echo.
    echo --- search_configurations TABLE ---
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.schema search_configurations
EOF
    echo.
    echo --- notifications_sent TABLE ---
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.schema notifications_sent
EOF
    goto :eof
)

if /i "!command!"=="stats" (
    echo.
    echo ===== DATABASE STATISTICS =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT 'Total Listings' as Metric, COUNT(*) as Count FROM seen_listings
UNION ALL
SELECT 'Listings (24h)', COUNT(*) FROM seen_listings WHERE created_at > datetime('now', '-1 day')
UNION ALL
SELECT 'Notifications (24h)', COUNT(*) FROM notifications_sent WHERE sent_at > datetime('now', '-1 day') AND success = 1
UNION ALL
SELECT 'Total Vehicles', COUNT(*) FROM vehicle_details
UNION ALL
SELECT 'Search Configs', COUNT(*) FROM search_configurations;
EOF
    goto :eof
)

if /i "!command!"=="listings" (
    set "limit=%2"
    if "!limit!"=="" set "limit=20"
    echo.
    echo ===== LATEST LISTINGS (Last !limit!) =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT id, created_at, notified FROM seen_listings ORDER BY created_at DESC LIMIT !limit!;
EOF
    goto :eof
)

if /i "!command!"=="listing" (
    set "id=%2"
    if "!id!"=="" (
        echo ERROR: Please provide listing ID
        echo Usage: query_db.bat listing ^<listing_id^>
        exit /b 1
    )
    echo.
    echo ===== LISTING DETAILS: !id! =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT * FROM seen_listings WHERE id = '!id!';
EOF
    echo.
    echo --- Vehicle Details ---
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT listing_id, make, model, year, price, currency, mileage_km, location, seller_name FROM vehicle_details WHERE listing_id = '!id!';
EOF
    goto :eof
)

if /i "!command!"=="notifications" (
    set "limit=%2"
    if "!limit!"=="" set "limit=20"
    echo.
    echo ===== NOTIFICATION LOGS (Last !limit!) =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT id, listing_id, notification_type, sent_at, success FROM notifications_sent ORDER BY sent_at DESC LIMIT !limit!;
EOF
    goto :eof
)

if /i "!command!"=="recent" (
    set "days=%2"
    if "!days!"=="" set "days=7"
    echo.
    echo ===== RECENTLY ADDED CARS (Last !days! days) =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT s.id, s.created_at, v.make, v.model, v.year, v.price, v.currency, v.location FROM seen_listings s LEFT JOIN vehicle_details v ON s.id = v.listing_id WHERE s.created_at > datetime('now', '-!days! days') ORDER BY s.created_at DESC;
EOF
    goto :eof
)

if /i "!command!"=="by-make" (
    echo.
    echo ===== CARS BY MAKE =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT make, COUNT(*) as count FROM vehicle_details WHERE make IS NOT NULL GROUP BY make ORDER BY count DESC;
EOF
    goto :eof
)

if /i "!command!"=="by-price" (
    echo.
    echo ===== CARS BY PRICE RANGE =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT
    CASE
        WHEN price < 5000 THEN 'Under 5K'
        WHEN price < 10000 THEN '5K-10K'
        WHEN price < 20000 THEN '10K-20K'
        WHEN price < 50000 THEN '20K-50K'
        ELSE 'Over 50K'
    END as price_range,
    COUNT(*) as count
FROM vehicle_details
WHERE price IS NOT NULL
GROUP BY price_range;
EOF
    goto :eof
)

if /i "!command!"=="search" (
    echo.
    echo ===== SEARCH CONFIGURATIONS =====
    echo.
    turso db shell "!TURSO_DATABASE_URL!" --auth-token="!TURSO_AUTH_TOKEN!" <<EOF
.headers on
.mode column
SELECT id, name, vehicle_make, vehicle_model, price_from, price_to, is_active FROM search_configurations;
EOF
    goto :eof
)

if /i "!command!"=="help" (
    cls
    echo.
    echo ============================================================
    echo  Turso Database Query Tool - Help
    echo ============================================================
    echo.
    echo Usage:
    echo   query_db.bat [command] [options]
    echo.
    echo Commands:
    echo.
    echo   tables              Show all database tables
    echo   schema              Show database schema
    echo   stats               Show database statistics
    echo   listings [limit]    Show all listings (default: 20)
    echo   listing ^<id^>       Show details for specific listing
    echo   notifications      Show notification logs
    echo   recent [days]      Show cars added in last N days (default: 7)
    echo   by-make            Show car count by make
    echo   by-price           Show car count by price range
    echo   search             Show search configurations
    echo   help               Show this help message
    echo.
    echo Examples:
    echo.
    echo   query_db.bat tables
    echo   query_db.bat stats
    echo   query_db.bat listings 50
    echo   query_db.bat listing 119084515
    echo   query_db.bat recent 30
    echo   query_db.bat by-make
    echo.
    echo Requirements:
    echo   - Turso CLI installed (https://docs.turso.tech/reference/turso-cli)
    echo   - TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env or .env.local
    echo.
    echo ============================================================
    echo.
    goto :eof
)

echo Unknown command: !command!
echo Run: query_db.bat help
exit /b 1
