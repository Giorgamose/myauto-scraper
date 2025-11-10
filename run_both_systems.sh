#!/bin/bash
# Run both the main monitoring system and the Telegram bot in parallel
# This keeps both systems independent and running simultaneously

echo "=========================================="
echo "MyAuto Listing Monitor - Dual System Runner"
echo "=========================================="
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ Error: .env.local not found"
    echo "Please create .env.local with TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check if required files exist
if [ ! -f main.py ]; then
    echo "❌ Error: main.py not found"
    exit 1
fi

if [ ! -f telegram_bot_main.py ]; then
    echo "❌ Error: telegram_bot_main.py not found"
    exit 1
fi

echo "✅ All required files found"
echo ""

# Display what will be run
echo "Starting both systems in parallel:"
echo ""
echo "System 1 - Main Monitoring"
echo "  Script:     main.py"
echo "  Purpose:    Predefined searches from config.json"
echo "  Database:   Supabase"
echo "  Command:    python main.py"
echo ""

echo "System 2 - Telegram Bot"
echo "  Script:     telegram_bot_main.py"
echo "  Purpose:    User-managed searches via Telegram commands"
echo "  Database:   Local SQLite (telegram_bot.db)"
echo "  Command:    python telegram_bot_main.py"
echo ""

echo "=========================================="
echo "Starting both systems now..."
echo "=========================================="
echo ""

# Start main system in background
echo "[1/2] Starting main monitoring system..."
python main.py &
MAIN_PID=$!
echo "      Main system PID: $MAIN_PID"
sleep 2

echo ""

# Start bot system in background
echo "[2/2] Starting Telegram bot system..."
python telegram_bot_main.py &
BOT_PID=$!
echo "      Bot system PID: $BOT_PID"
sleep 2

echo ""
echo "=========================================="
echo "✅ Both systems are now running!"
echo "=========================================="
echo ""

echo "Active Processes:"
echo "  - Main system (PID: $MAIN_PID): python main.py"
echo "  - Bot system (PID: $BOT_PID): python telegram_bot_main.py"
echo ""

echo "Status:"
echo "  ✓ Predefined searches from config.json are being monitored"
echo "  ✓ Telegram bot is listening for /set /list /clear commands"
echo "  ✓ Both systems can send notifications independently"
echo ""

echo "To stop both systems, press Ctrl+C"
echo ""

# Wait for both processes
wait $MAIN_PID $BOT_PID

echo ""
echo "=========================================="
echo "Both systems have stopped"
echo "=========================================="
