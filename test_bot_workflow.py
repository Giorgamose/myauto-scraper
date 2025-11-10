#!/usr/bin/env python3
"""
Test Bot Workflow: /list -> /set -> /run
Simulates the complete bot workflow
"""

import logging
from dotenv import load_dotenv
import os

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("BOT WORKFLOW TEST")
print("=" * 80)
print()

try:
    # Initialize all components
    from telegram_bot_database_supabase import TelegramBotDatabaseSupabase
    from telegram_bot_backend import TelegramBotBackend
    from utils import load_config_file, get_config_path
    from scraper import MyAutoScraper

    chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

    print("[*] Initializing components...")
    db = TelegramBotDatabaseSupabase()
    config = load_config_file(get_config_path())
    scraper = MyAutoScraper(config)

    bot = TelegramBotBackend(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        database=db,
        scraper=scraper,
        config=config
    )
    print("[OK] All components initialized")
    print()

    # Test 1: /list command
    print("-" * 80)
    print("TEST 1: /list (List all subscriptions)")
    print("-" * 80)

    message = {"chat": {"id": chat_id}, "text": "/list"}
    print(f"[*] Sending: /list")
    print(f"[*] Chat ID: {chat_id}")

    try:
        result = bot.process_message(message)
        print(f"[OK] Command processed (result: {result})")
    except Exception as e:
        print(f"[ERROR] Error processing /list: {e}")
        import traceback
        traceback.print_exc()

    # Get current subscriptions
    subs = db.get_subscriptions(chat_id)
    print(f"\n[*] Current subscriptions in database: {len(subs)}")
    for i, sub in enumerate(subs, 1):
        print(f"    {i}. ID: {sub.get('id')}")
        print(f"       URL: {sub.get('search_url')[:70]}...")
        print(f"       Active: {sub.get('is_active')}")

    print()

    # Test 2: /set command
    if len(subs) == 0:
        print("-" * 80)
        print("TEST 2: /set (Add a new subscription)")
        print("-" * 80)

        test_url = "https://myauto.ge/ka/s/iyideba-motociklebi-ktm-690-smc?vehicleType=2&bargainType=0&mansNModels=105.3177&currId=1&mileageType=1&customs=1&page=1&layoutId=1"

        message = {"chat": {"id": chat_id}, "text": f"/set {test_url}"}
        print(f"[*] Sending: /set <url>")
        print(f"[*] URL: {test_url[:60]}...")

        try:
            result = bot.process_message(message)
            print(f"[OK] Command processed (result: {result})")
        except Exception as e:
            print(f"[ERROR] Error processing /set: {e}")
            import traceback
            traceback.print_exc()

        # Verify subscription was added
        subs = db.get_subscriptions(chat_id)
        print(f"\n[*] Subscriptions after /set: {len(subs)}")
        for i, sub in enumerate(subs, 1):
            print(f"    {i}. ID: {sub.get('id')}")
            print(f"       URL: {sub.get('search_url')[:70]}...")

        print()

    # Test 3: /run command
    if len(subs) > 0:
        print("-" * 80)
        print("TEST 3: /run 1 (Execute first subscription)")
        print("-" * 80)

        message = {"chat": {"id": chat_id}, "text": "/run 1"}
        print(f"[*] Sending: /run 1")
        print(f"[*] Will execute first subscription")

        try:
            result = bot.process_message(message)
            print(f"[OK] Command processed (result: {result})")
        except Exception as e:
            print(f"[ERROR] Error processing /run: {e}")
            import traceback
            traceback.print_exc()

        print()

    # Test 4: /status command
    print("-" * 80)
    print("TEST 4: /status (Show statistics)")
    print("-" * 80)

    message = {"chat": {"id": chat_id}, "text": "/status"}
    print(f"[*] Sending: /status")

    try:
        result = bot.process_message(message)
        print(f"[OK] Command processed (result: {result})")
    except Exception as e:
        print(f"[ERROR] Error processing /status: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
