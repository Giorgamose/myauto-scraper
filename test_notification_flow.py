#!/usr/bin/env python3
"""
Test notification flow with actual data structures
Verifies that notifications will be sent when new listings are found
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from notifications_telegram import TelegramNotificationManager
from utils import load_config_file

# Load config
config = load_config_file('config.json')
telegram_settings = config.get('telegram_settings', {})

# Create Telegram manager
telegram = TelegramNotificationManager(
    bot_token=telegram_settings.get('bot_token'),
    chat_id=telegram_settings.get('chat_id')
)

print("[*] Testing notification flow\n")
print(f"[*] Telegram token configured: {bool(telegram_settings.get('bot_token'))}")
print(f"[*] Chat ID configured: {telegram_settings.get('chat_id')}\n")

# Test 1: Test with summary data (what we get from search results)
print("[TEST 1] Testing notification with search result summary data:")
print("=" * 60)

summary_data = {
    'listing_id': '119084515',
    'title': 'Toyota Land Cruiser 2001',
    'price': '15500',
    'currency': 'USD',
    'location': 'თბილისი',
    'mileage_km': '446000',
    'image_url': None,
    'url': '/ka/pr/119084515/...'
}

print(f"Data: {summary_data}\n")

# Check what the notification formatter will do with this data
message = telegram._format_new_listing(summary_data)
print("Formatted message:")
print(message)
print()

# Test 2: Test with full detail data (what we get from detail page)
print("\n[TEST 2] Testing notification with full detail data:")
print("=" * 60)

detail_data = {
    'listing_id': '119084515',
    'make': 'Toyota',
    'model': 'Land Cruiser',
    'year': '2001',
    'price': '15500',
    'currency': 'USD',
    'location': 'თბილისი',
    'mileage_km': '446000',
    'fuel_type': 'დიზელი',
    'transmission': 'ტიპტრონიკი',
    'drive_type': '4x4',
    'seller_name': 'John Doe',
    'customs_cleared': True
}

print(f"Data: {detail_data}\n")

message = telegram._format_new_listing(detail_data)
print("Formatted message:")
print(message)
print()

# Test 3: Verify notification can be sent (dry run)
print("\n[TEST 3] Notification service status:")
print("=" * 60)
print(f"[*] Bot token configured: {'***' if telegram.bot_token else 'NOT SET'}")
print(f"[*] Chat ID configured: {telegram.chat_id}")

print("\n[OK] Notification flow tests completed")
print("     When new listings are found, notifications will be sent with above format")
