#!/usr/bin/env python3
"""
Test Telegram Bot Connection
Simple, free, unlimited notifications
"""

import requests
import json
import urllib3

# Suppress SSL warnings (needed for testing environments with certificate issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Your Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN = "8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4"  # Example: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Your Telegram User/Chat ID (get by sending /start to your bot)
TELEGRAM_CHAT_ID = "-1003275746217"  # Example: 987654321

def send_telegram_message(token, chat_id, message, parse_mode="HTML"):
    """
    Send a message via Telegram Bot API

    Args:
        token: Telegram Bot token
        chat_id: Your Telegram chat/user ID
        message: Message text (supports HTML formatting)
        parse_mode: HTML or Markdown
    """

    print("[*] TELEGRAM MESSAGE TEST")
    print("=" * 60)

    # Validate inputs
    if token == "YOUR_BOT_TOKEN_HERE" or chat_id == "YOUR_CHAT_ID_HERE":
        print("[ERROR] Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first!")
        print("\nSteps:")
        print("  1. Create bot: Message @BotFather on Telegram")
        print("  2. Get token from BotFather")
        print("  3. Send /start to your bot")
        print("  4. Check received message in meta.py (script will show chat_id)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }

    try:
        print(f"\n[1] Sending message to chat ID: {chat_id}")
        print(f"    Message preview: {message[:50]}...")

        response = requests.post(url, json=payload, timeout=10, verify=False)

        print(f"\n[2] Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                print(f"[OK] Message sent successfully!")
                print(f"    Message ID: {message_id}")
                print("\n" + "=" * 60)
                print("[OK] TELEGRAM BOT IS WORKING!")
                print("=" * 60)
                return True
            else:
                print(f"[ERROR] Telegram API error: {result.get('description')}")
                return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to Telegram API")
        print("        Check your internet connection")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False

def get_telegram_updates(token):
    """
    Get latest messages (to find your chat ID)
    """

    print("\n[*] GETTING TELEGRAM UPDATES")
    print("=" * 60)

    url = f"https://api.telegram.org/bot{token}/getUpdates"

    try:
        response = requests.get(url, timeout=10, verify=False)

        if response.status_code == 200:
            updates = response.json()

            if not updates.get("ok"):
                print("[ERROR] Could not get updates")
                return None

            messages = updates.get("result", [])

            if not messages:
                print("[WARN] No messages found")
                print("       Send /start to your bot first!")
                return None

            # Get the latest message
            latest = messages[-1]
            chat_id = latest["message"]["chat"]["id"]
            username = latest["message"]["chat"].get("username", "N/A")

            print(f"[OK] Found chat!")
            print(f"    Chat ID: {chat_id}")
            print(f"    Username: @{username}")

            return chat_id

        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return None

def main():
    """Main test"""

    print("\n" + "=" * 60)
    print("TELEGRAM BOT CONNECTION TEST")
    print("=" * 60)

    # Step 1: Get token from user
    print("\n[SETUP] Telegram Bot Token Setup")
    print("  1. Go to Telegram and search for: @BotFather")
    print("  2. Send: /newbot")
    print("  3. Follow prompts to create bot")
    print("  4. Copy the token provided")
    print("  5. Replace TELEGRAM_BOT_TOKEN in this file")

    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n[ERROR] Token not set!")
        return 1

    # Step 2: Get chat ID
    print("\n[SETUP] Getting your Chat ID...")
    print("  1. Open your Telegram bot (search for it)")
    print("  2. Send: /start")
    print("  3. Wait for response...")

    chat_id = get_telegram_updates(TELEGRAM_BOT_TOKEN)

    if chat_id:
        print(f"\n[INFO] Update this file with:")
        print(f"    TELEGRAM_CHAT_ID = {chat_id}")
    else:
        print("\n[ERROR] Could not find chat ID")
        print("        Make sure you've messaged your bot")
        return 1

    # Step 3: Send test message
    print("\n[TEST] Sending test message...")

    test_message = """
<b>[CAR] MyAuto Car Listing Monitor</b>

<b>Test Message</b>
This is a test message from your scraper!

If you see this, Telegram bot is working correctly.

<b>Features:</b>
- Unlimited free messages
- Rich formatting (bold, italic, links)
- Send images from listings
- Completely free forever
    """.strip()

    success = send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id or TELEGRAM_CHAT_ID, test_message)

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
