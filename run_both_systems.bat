@echo off
REM Run both the main monitoring system and the Telegram bot in parallel
REM This keeps both systems independent and running simultaneously

setlocal enabledelayedexpansion

echo ==========================================
echo MyAuto Listing Monitor - Dual System Runner
echo ==========================================
echo.

REM Check if .env.local exists
if not exist .env.local (
    echo Error: .env.local not found
    echo Please create .env.local with TELEGRAM_BOT_TOKEN
    pause
    exit /b 1
)

REM Check if required files exist
if not exist main.py (
    echo Error: main.py not found
    pause
    exit /b 1
)

if not exist telegram_bot_main.py (
    echo Error: telegram_bot_main.py not found
    pause
    exit /b 1
)

echo OK: All required files found
echo.

REM Display what will be run
echo Starting both systems in parallel:
echo.
echo System 1 - Main Monitoring
echo   Script:     main.py
echo   Purpose:    Predefined searches from config.json
echo   Database:   Supabase
echo.

echo System 2 - Telegram Bot
echo   Script:     telegram_bot_main.py
echo   Purpose:    User-managed searches via Telegram commands
echo   Database:   Local SQLite (telegram_bot.db)
echo.

echo ==========================================
echo Starting both systems now...
echo ==========================================
echo.

REM Start both systems in separate windows
echo [1/2] Starting main monitoring system in new window...
start "MyAuto Main Monitor" cmd /k python main.py
timeout /t 2 /nobreak

echo [2/2] Starting Telegram bot system in new window...
start "MyAuto Telegram Bot" cmd /k python telegram_bot_main.py
timeout /t 2 /nobreak

echo.
echo ==========================================
echo OK: Both systems are now running!
echo ==========================================
echo.

echo Active Systems:
echo   - Main system: python main.py (in "MyAuto Main Monitor" window)
echo   - Bot system: python telegram_bot_main.py (in "MyAuto Telegram Bot" window)
echo.

echo Status:
echo   OK: Predefined searches from config.json are being monitored
echo   OK: Telegram bot is listening for /set /list /clear commands
echo   OK: Both systems can send notifications independently
echo.

echo View the separate windows to see logs from each system.
echo To stop both systems, close both windows or press Ctrl+C in each.
echo.

pause
