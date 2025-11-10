#!/usr/bin/env python3
"""
Debug script to check what's in the bot database
"""

import logging
from dotenv import load_dotenv
from urllib.parse import quote
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load env
load_dotenv('.env.local')
load_dotenv('.env')

print("=" * 80)
print("TELEGRAM BOT DATABASE DEBUG")
print("=" * 80)
print()

try:
    # Connect to database
    db = TelegramBotDatabaseSupabase()
    print("✅ Connected to Supabase")
    print()

    # Get all subscriptions for your chat
    chat_id = 6366712840  # Your personal chat ID (adjust if different)
    print(f"Checking subscriptions for chat_id: {chat_id}")
    print("-" * 80)

    subs = db.get_subscriptions(chat_id)

    print(f"✅ Found {len(subs)} ACTIVE subscriptions:")
    for i, sub in enumerate(subs, 1):
        print(f"\n   {i}. ID: {sub.get('id')}")
        print(f"      Chat ID: {sub.get('chat_id')}")
        print(f"      URL: {sub.get('search_url')}")
        print(f"      Active: {sub.get('is_active')}")
        print(f"      Created: {sub.get('created_at')}")
        print(f"      Last Checked: {sub.get('last_checked')}")

    print()
    print("-" * 80)
    print()

    # Now check ALL subscriptions (active and inactive) for this chat
    print(f"Checking ALL subscriptions (active + inactive) for chat_id: {chat_id}")
    print("-" * 80)

    # Query all subscriptions directly
    filter_str = f"chat_id=eq.{chat_id}&order=created_at.desc"
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_subscriptions?{filter_str}",
        headers=db.db.headers,
        timeout=10
    )

    if response.status_code == 200:
        all_subs = response.json()
        print(f"✅ Found {len(all_subs)} TOTAL subscriptions (active + inactive):")
        for i, sub in enumerate(all_subs, 1):
            active_status = "🟢 ACTIVE" if sub.get('is_active') else "🔴 INACTIVE"
            print(f"\n   {i}. {active_status}")
            print(f"      ID: {sub.get('id')}")
            print(f"      URL: {sub.get('search_url')}")
            print(f"      Created: {sub.get('created_at')}")
            print(f"      Last Checked: {sub.get('last_checked')}")
    else:
        print(f"❌ Failed to query all subscriptions: {response.status_code}")
        print(f"   Error: {response.text}")

    print()
    print("-" * 80)
    print()

    # Test the add_subscription logic
    test_url = "https://myauto.ge/ka/s/iyideba-motociklebi-ktm-690-smc?vehicleType=2&bargainType=0&mansNModels=105.3177&currId=1&mileageType=1&customs=1&page=1&layoutId=1"

    print(f"Testing add_subscription with test URL:")
    print(f"URL: {test_url[:80]}...")
    print("-" * 80)

    # Check if it exists (with URL encoding)
    encoded_url = quote(test_url, safe='')
    filter_str = f"chat_id=eq.{chat_id}&search_url=eq.{encoded_url}"
    check_response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_subscriptions?{filter_str}",
        headers=db.db.headers,
        timeout=10
    )

    existing_subs = check_response.json() if check_response.status_code == 200 else []

    if existing_subs:
        existing = existing_subs[0]
        is_active = existing.get("is_active", True)
        print(f"❌ Subscription EXISTS:")
        print(f"   ID: {existing.get('id')}")
        print(f"   Active: {is_active}")
        print(f"   Created: {existing.get('created_at')}")
        print()
        if is_active:
            print("   → Result: Would return False (Already monitoring)")
        else:
            print("   → Result: Would attempt to reactivate")
    else:
        print("✅ Subscription does NOT exist")
        print("   → Result: Would create new subscription")

    print()
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
