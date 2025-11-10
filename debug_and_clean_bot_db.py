#!/usr/bin/env python3
"""
Debug and Clean Telegram Bot Database
Shows what's in the database and optionally cleans it
"""

import logging
from dotenv import load_dotenv

# Load env
load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TELEGRAM BOT DATABASE DEBUG & CLEANUP")
print("=" * 80)
print()

try:
    from telegram_bot_database_supabase import TelegramBotDatabaseSupabase

    # Connect to database
    print("[*] Connecting to Supabase...")
    db = TelegramBotDatabaseSupabase()
    print("[OK] Connected to Supabase")
    print()

    # ========== GET ALL DATA ==========
    print("=" * 80)
    print("CURRENT DATABASE STATE")
    print("=" * 80)
    print()

    # 1. Check subscriptions
    print("[1] SUBSCRIPTIONS")
    print("-" * 80)
    filter_str = "order=created_at.desc"
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_subscriptions?{filter_str}",
        headers=db.db.headers,
        timeout=10
    )

    subscriptions = response.json() if response.status_code == 200 else []
    print(f"Total subscriptions: {len(subscriptions)}")
    print()

    if subscriptions:
        for i, sub in enumerate(subscriptions, 1):
            is_active = "🟢 ACTIVE" if sub.get('is_active') else "🔴 INACTIVE"
            print(f"{i}. {is_active}")
            print(f"   ID: {sub.get('id')}")
            print(f"   Chat ID: {sub.get('chat_id')}")
            print(f"   URL: {sub.get('search_url')[:80]}...")
            print(f"   Created: {sub.get('created_at')}")
            print(f"   Last Checked: {sub.get('last_checked')}")
            print()

    # 2. Check seen listings
    print("[2] SEEN LISTINGS")
    print("-" * 80)
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/user_seen_listings?order=seen_at.desc",
        headers=db.db.headers,
        timeout=10
    )

    seen_listings = response.json() if response.status_code == 200 else []
    print(f"Total seen listings: {len(seen_listings)}")
    print()

    if seen_listings:
        # Group by chat_id
        by_chat = {}
        for listing in seen_listings:
            chat_id = listing.get('chat_id')
            if chat_id not in by_chat:
                by_chat[chat_id] = []
            by_chat[chat_id].append(listing)

        for chat_id, listings in by_chat.items():
            print(f"Chat ID {chat_id}: {len(listings)} seen listings")
            for j, listing in enumerate(listings[:5], 1):  # Show first 5
                print(f"  {j}. {listing.get('listing_id')} (seen: {listing.get('seen_at')})")
            if len(listings) > 5:
                print(f"  ... and {len(listings) - 5} more")
            print()

    # 3. Check events
    print("[3] BOT EVENTS (Logs)")
    print("-" * 80)
    response = db.db._make_request(
        'GET',
        f"{db.db.base_url}/bot_events?order=created_at.desc&limit=20",
        headers=db.db.headers,
        timeout=10
    )

    events = response.json() if response.status_code == 200 else []
    print(f"Total recent events: {len(events)}")
    print()

    if events:
        for i, event in enumerate(events[:10], 1):  # Show first 10
            print(f"{i}. {event.get('event_type')} (Chat: {event.get('chat_id')})")
            print(f"   Time: {event.get('created_at')}")
            print()

    # ========== SUMMARY ==========
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total subscriptions: {len(subscriptions)}")
    print(f"  - Active: {sum(1 for s in subscriptions if s.get('is_active'))}")
    print(f"  - Inactive: {sum(1 for s in subscriptions if not s.get('is_active'))}")
    print(f"Total seen listings: {len(seen_listings)}")
    print(f"Total events: {len(events)}")
    print()

    # ========== ASK TO CLEAN ==========
    print("=" * 80)
    print("CLEANUP OPTIONS")
    print("=" * 80)
    print()
    print("What would you like to do?")
    print()
    print("1. Delete ALL seen listings (bot will re-notify about old listings)")
    print("2. Delete ALL subscriptions (bot will have no searches)")
    print("3. Delete EVERYTHING (complete reset)")
    print("4. Delete specific user's data")
    print("5. Do nothing (just debug, no changes)")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        print()
        print("[*] Deleting all seen listings...")
        response = db.db._make_request(
            'DELETE',
            f"{db.db.base_url}/user_seen_listings",
            headers=db.db.headers,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print("[OK] Deleted all seen listings!")
            # Verify
            response = db.db._make_request(
                'GET',
                f"{db.db.base_url}/user_seen_listings?limit=1",
                headers=db.db.headers,
                timeout=10
            )
            remaining = len(response.json() if response.status_code == 200 else [])
            print(f"[OK] Remaining seen listings: {remaining}")
        else:
            print(f"[ERROR] Failed to delete: {response.status_code}")

    elif choice == "2":
        print()
        print("[*] Deleting all subscriptions...")
        response = db.db._make_request(
            'DELETE',
            f"{db.db.base_url}/user_subscriptions",
            headers=db.db.headers,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print("[OK] Deleted all subscriptions!")
            # Verify
            response = db.db._make_request(
                'GET',
                f"{db.db.base_url}/user_subscriptions?limit=1",
                headers=db.db.headers,
                timeout=10
            )
            remaining = len(response.json() if response.status_code == 200 else [])
            print(f"[OK] Remaining subscriptions: {remaining}")
        else:
            print(f"[ERROR] Failed to delete: {response.status_code}")

    elif choice == "3":
        print()
        print("[!] COMPLETE RESET - Deleting ALL data...")
        confirm = input("Are you SURE? Type 'YES' to confirm: ").strip()

        if confirm == "YES":
            # Delete in order (subscriptions first, then seen_listings, then events)
            print("[*] Deleting seen listings...")
            db.db._make_request(
                'DELETE',
                f"{db.db.base_url}/user_seen_listings",
                headers=db.db.headers,
                timeout=10
            )

            print("[*] Deleting events...")
            db.db._make_request(
                'DELETE',
                f"{db.db.base_url}/bot_events",
                headers=db.db.headers,
                timeout=10
            )

            print("[*] Deleting subscriptions...")
            db.db._make_request(
                'DELETE',
                f"{db.db.base_url}/user_subscriptions",
                headers=db.db.headers,
                timeout=10
            )

            print("[OK] Complete reset done!")
            print()
            print("[OK] All tables are now empty")
            print("[*] You can now add fresh searches with /set")

        else:
            print("Cancelled.")

    elif choice == "4":
        print()
        chat_id = input("Enter chat ID to delete (e.g., 6366712840): ").strip()

        try:
            chat_id = int(chat_id)
            print(f"[*] Deleting data for chat {chat_id}...")

            # Delete seen listings for this user
            response = db.db._make_request(
                'DELETE',
                f"{db.db.base_url}/user_seen_listings?chat_id=eq.{chat_id}",
                headers=db.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                print(f"[OK] Deleted seen listings for chat {chat_id}")
            else:
                print(f"[ERROR] Failed to delete: {response.status_code}")

            # Delete subscriptions for this user
            response = db.db._make_request(
                'DELETE',
                f"{db.db.base_url}/user_subscriptions?chat_id=eq.{chat_id}",
                headers=db.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                print(f"[OK] Deleted subscriptions for chat {chat_id}")
            else:
                print(f"[ERROR] Failed to delete: {response.status_code}")

        except ValueError:
            print("Invalid chat ID")

    elif choice == "5":
        print()
        print("[*] No changes made")

    else:
        print("Invalid choice")

    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Stop the bot: Ctrl+C")
    print("2. Restart the bot: python telegram_bot_main.py")
    print("3. Test with fresh commands:")
    print("   /set <myauto-url>")
    print("   /run 1")
    print()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
