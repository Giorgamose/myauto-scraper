#!/usr/bin/env python3
"""
Comprehensive Bot Diagnostics
Tests all bot components to identify what's broken
"""

import logging
from dotenv import load_dotenv
import os

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("TELEGRAM BOT DIAGNOSTICS")
print("=" * 80)
print()

# ============================================================================
# TEST 1: Check Environment Variables
# ============================================================================
print("[TEST 1] ENVIRONMENT VARIABLES")
print("-" * 80)

required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
    'SUPABASE_URL',
    'SUPABASE_API_KEY'
]

all_vars_ok = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first/last chars only for security
        if len(value) > 20:
            display = f"{value[:10]}...{value[-5:]}"
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: NOT SET")
        all_vars_ok = False

if not all_vars_ok:
    print("\n[ERROR] Missing environment variables. Update .env.local")
    exit(1)

print()

# ============================================================================
# TEST 2: Check Supabase Connection
# ============================================================================
print("[TEST 2] SUPABASE CONNECTION")
print("-" * 80)

try:
    from telegram_bot_database_supabase import TelegramBotDatabaseSupabase

    print("[*] Connecting to Supabase...")
    db = TelegramBotDatabaseSupabase()
    print("✅ Supabase connected successfully")

    # Test a simple query
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_subscriptions?limit=1",
        headers=db.db.headers,
        timeout=10
    )

    if response.status_code == 200:
        print(f"✅ Database query successful (status: {response.status_code})")
    else:
        print(f"⚠️ Database query returned status: {response.status_code}")

except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# ============================================================================
# TEST 3: Check Bot Token
# ============================================================================
print("[TEST 3] TELEGRAM BOT TOKEN")
print("-" * 80)

try:
    import requests
    import warnings
    import urllib3

    warnings.filterwarnings('ignore')
    urllib3.disable_warnings()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Try with SSL verification first
    try:
        response = requests.post(f"https://api.telegram.org/bot{token}/getMe", timeout=5, verify=True)
    except requests.exceptions.SSLError:
        # Retry without SSL verification
        print("[*] SSL error, retrying without verification...")
        response = requests.post(f"https://api.telegram.org/bot{token}/getMe", timeout=5, verify=False)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot token valid")
            print(f"   Bot username: @{bot_info.get('username')}")
            print(f"   Bot name: {bot_info.get('first_name')}")
            bot_valid = True
        else:
            print(f"❌ Bot token invalid: {data.get('description')}")
            bot_valid = False
    else:
        print(f"❌ Failed to verify bot token (HTTP {response.status_code})")
        bot_valid = False

except Exception as e:
    print(f"❌ Error checking bot token: {e}")
    bot_valid = False

print()

# ============================================================================
# TEST 4: Check Scraper
# ============================================================================
print("[TEST 4] SCRAPER")
print("-" * 80)

try:
    from utils import load_config_file, get_config_path

    print("[*] Loading config...")
    config_path = get_config_path()
    config = load_config_file(config_path)

    if config:
        print("✅ Configuration loaded successfully")
    else:
        print("⚠️ Configuration is empty")

    print("[*] Initializing scraper...")
    from scraper import MyAutoScraper

    scraper = MyAutoScraper(config)
    print("✅ Scraper initialized successfully")
    scraper_ok = True

except Exception as e:
    print(f"⚠️ Scraper initialization issue: {e}")
    scraper_ok = False

print()

# ============================================================================
# TEST 5: Check Bot Backend
# ============================================================================
print("[TEST 5] BOT BACKEND")
print("-" * 80)

try:
    from telegram_bot_backend import TelegramBotBackend

    print("[*] Creating bot backend...")
    bot = TelegramBotBackend(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        database=db,
        scraper=scraper if scraper_ok else None,
        config=config if scraper_ok else None
    )
    print("✅ Bot backend created successfully")
    backend_ok = True

except Exception as e:
    print(f"❌ Bot backend error: {e}")
    import traceback
    traceback.print_exc()
    backend_ok = False

print()

# ============================================================================
# TEST 6: Test Bot Commands (Simulation)
# ============================================================================
print("[TEST 6] BOT COMMAND ROUTING")
print("-" * 80)

if backend_ok:
    try:
        test_chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

        # Simulate /help command
        print("[*] Testing /help command...")
        message_obj = {
            "chat": {"id": test_chat_id},
            "text": "/help"
        }

        result = bot.process_message(message_obj)
        if result:
            print("✅ /help command processed")
        else:
            print("⚠️ /help command returned False")

        # Simulate /list command
        print("[*] Testing /list command...")
        message_obj["text"] = "/list"

        result = bot.process_message(message_obj)
        if result:
            print("✅ /list command processed")
        else:
            print("⚠️ /list command returned False")

        # Simulate /status command
        print("[*] Testing /status command...")
        message_obj["text"] = "/status"

        result = bot.process_message(message_obj)
        if result:
            print("✅ /status command processed")
        else:
            print("⚠️ /status command returned False")

    except Exception as e:
        print(f"❌ Error testing commands: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️ Skipping command tests (backend not initialized)")

print()

# ============================================================================
# TEST 7: Database Subscriptions
# ============================================================================
print("[TEST 7] DATABASE STATE")
print("-" * 80)

try:
    chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

    subs = db.get_subscriptions(chat_id)
    print(f"✅ Subscriptions for chat {chat_id}: {len(subs)}")

    if subs:
        for i, sub in enumerate(subs, 1):
            active = "🟢" if sub.get('is_active') else "🔴"
            print(f"   {i}. {active} ID: {sub.get('id')}")
            print(f"      URL: {sub.get('search_url')[:60]}...")

    # Count seen listings
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_seen_listings?chat_id=eq.{chat_id}&limit=1",
        headers=db.db.headers,
        timeout=10
    )

    if response.status_code == 200:
        seen = response.json()
        print(f"✅ Seen listings for this chat: {len(seen)}")

except Exception as e:
    print(f"⚠️ Error checking database: {e}")

print()

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================
print("=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)
print()

if all_vars_ok and bot_valid and backend_ok:
    print("✅ All diagnostics passed!")
    print()
    print("If bot is still not responding:")
    print("1. Check if bot is actually running: python telegram_bot_main.py")
    print("2. Check terminal logs for errors")
    print("3. Verify you're messaging the correct bot: @myauto_listining_bot")
    print("4. Give the bot permission to post messages in the channel")
    print("5. Check that Telegram chat ID is correct: " + str(os.getenv("TELEGRAM_CHAT_ID")))
else:
    print("❌ Issues detected:")
    if not all_vars_ok:
        print("   - Missing environment variables")
    if not bot_valid:
        print("   - Bot token invalid or Telegram API unreachable")
    if not backend_ok:
        print("   - Bot backend has errors")
    print()
    print("Fix these issues and try again")

print()
print("=" * 80)
