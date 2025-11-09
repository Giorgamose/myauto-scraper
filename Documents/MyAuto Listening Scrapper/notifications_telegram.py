#!/usr/bin/env python3
"""
Telegram Notifications Handler
Send car listing notifications via Telegram Bot
"""

import requests
import os
import logging
import warnings
import urllib3
from datetime import datetime

# Suppress SSL warnings for test environments
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotificationManager:
    """Send notifications via Telegram Bot API"""

    def __init__(self, bot_token=None, chat_id=None, verify_ssl=True):
        """
        Initialize Telegram bot credentials

        Args:
            bot_token: Telegram bot token (from env if None)
            chat_id: Telegram chat ID (from env if None)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        # Allow override via parameters or environment variables
        self.telegram_bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.verify_ssl = verify_ssl

        # Keep bot_token/chat_id as properties for backward compatibility
        self._bot_token = self.telegram_bot_token
        self._chat_id = self.telegram_chat_id

        # Only validate if not testing (credentials might be added later)
        if self._bot_token and self._chat_id:
            try:
                self._chat_id = int(self._chat_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid chat_id format: {self._chat_id}")

        self._update_api_url()

    def _update_api_url(self):
        """Update API URL based on current token"""
        if self._bot_token:
            self.api_url = f"https://api.telegram.org/bot{self._bot_token}"
        else:
            self.api_url = None

    @property
    def bot_token(self):
        """Get bot token"""
        return self._bot_token or self.telegram_bot_token

    @bot_token.setter
    def bot_token(self, value):
        """Set bot token"""
        self._bot_token = value
        self.telegram_bot_token = value
        self._update_api_url()

    @property
    def chat_id(self):
        """Get chat ID"""
        return self._chat_id or self.telegram_chat_id

    @chat_id.setter
    def chat_id(self, value):
        """Set chat ID"""
        self._chat_id = value
        self.telegram_chat_id = value

    def send_message(self, message_text, parse_mode="HTML"):
        """
        Send a text message to Telegram

        Args:
            message_text: Message content (supports HTML formatting)
            parse_mode: "HTML" or "Markdown"

        Returns:
            True if sent successfully, False otherwise
        """

        if not self.api_url or not self.chat_id:
            logger.error("Telegram credentials not configured (token or chat_id missing)")
            return False

        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": int(self.chat_id) if self.chat_id else None,
            "text": message_text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(url, json=payload, timeout=10, verify=self.verify_ssl)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    message_id = result["result"]["message_id"]
                    logger.info(f"[OK] Message sent: {message_id}")
                    return True
                else:
                    logger.error(f"Telegram error: {result.get('description')}")
                    return False
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False

    def send_photo(self, photo_url, caption=None, parse_mode="HTML"):
        """
        Send a photo to Telegram

        Args:
            photo_url: URL of the photo (must be HTTPS)
            caption: Photo caption (optional, supports HTML)
            parse_mode: "HTML" or "Markdown"

        Returns:
            True if sent successfully, False otherwise
        """

        if not self.api_url or not self.chat_id:
            logger.error("Telegram credentials not configured (token or chat_id missing)")
            return False

        url = f"{self.api_url}/sendPhoto"

        payload = {
            "chat_id": int(self.chat_id) if self.chat_id else None,
            "photo": photo_url,
            "parse_mode": parse_mode
        }

        if caption:
            payload["caption"] = caption

        try:
            response = requests.post(url, json=payload, timeout=10, verify=self.verify_ssl)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"[OK] Photo sent")
                    return True
                else:
                    logger.error(f"Telegram error: {result.get('description')}")
                    return False
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False

    def send_new_listing_notification(self, car_data):
        """Send notification for a single new listing"""

        message = self._format_new_listing(car_data)
        return self.send_message(message)

    def send_new_listings_notification(self, cars_list):
        """Send notification for multiple new listings"""

        if len(cars_list) == 1:
            return self.send_new_listing_notification(cars_list[0])

        message = self._format_multiple_listings(cars_list)
        return self.send_message(message)

    def send_status_notification(self, num_listings_checked=0):
        """Send heartbeat/status notification"""

        message = self._format_status(num_listings_checked)
        return self.send_message(message)

    def send_error_notification(self, error_text, search_name=None):
        """Send error notification"""

        message = self._format_error(error_text, search_name)
        return self.send_message(message)

    @staticmethod
    def _format_new_listing(car):
        """Format single car listing for Telegram"""

        # Format price with thousands separator
        price = car.get('price', 'N/A')
        if isinstance(price, (int, float)):
            price_str = f"${price:,.0f}"
        else:
            price_str = f"${price}"

        # Format mileage with thousands separator
        mileage = car.get('mileage_km', 'N/A')
        if isinstance(mileage, (int, float)):
            mileage_str = f"{mileage:,.0f} km"
        else:
            mileage_str = f"{mileage} km" if mileage != 'N/A' else "N/A"

        return f"""
<b>🚗 NEW CAR LISTING!</b>

<b>{car.get('make', 'Unknown')} {car.get('model', '')} {car.get('year', '')}</b>

<b>💰 Price:</b> {price_str} {car.get('currency', 'USD')}
<b>📍 Location:</b> {car.get('location', 'N/A')}
<b>🛣️ Mileage:</b> {mileage_str}
<b>⛽ Fuel:</b> {car.get('fuel_type', 'N/A')}
<b>🔄 Transmission:</b> {car.get('transmission', 'N/A')}
<b>🚙 Drive Type:</b> {car.get('drive_type', 'N/A')}

{('✅ Customs Cleared' if car.get('customs_cleared') else '⚠️ Customs Status Unknown')}

👤 <b>Seller:</b> {car.get('seller_name', 'N/A')}
📅 <b>Posted:</b> {car.get('posted_date', 'N/A')}

<a href="{car.get('url', '#')}">View full listing</a>
        """.strip()

    @staticmethod
    def _format_multiple_listings(cars_list):
        """Format multiple listings for Telegram"""

        message = f"<b>🎉 {len(cars_list)} NEW CAR LISTINGS!</b>\n\n"

        for i, car in enumerate(cars_list[:10], 1):
            # Format price safely
            price = car.get('price', 'N/A')
            price_str = f"${price:,.0f}" if isinstance(price, (int, float)) else f"${price}"

            # Format mileage safely
            mileage = car.get('mileage_km', 'N/A')
            mileage_str = f"{mileage:,.0f}" if isinstance(mileage, (int, float)) else f"{mileage}"

            message += f"<b>{i}. {car.get('make', 'Unknown')} {car.get('model', '')} {car.get('year', '')}</b>\n"
            message += f"   💰 {price_str} | 📍 {car.get('location', 'N/A')}\n"
            message += f"   🛣️ {mileage_str} km | ⛽ {car.get('fuel_type', 'N/A')}\n"
            message += f"   <a href=\"{car.get('url', '#')}\">View listing</a>\n\n"

        if len(cars_list) > 10:
            message += f"<i>...and {len(cars_list) - 10} more listings!</i>\n"

        return message.strip()

    @staticmethod
    def _format_status(num_listings=0):
        """Format status message"""

        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        return f"""
<b>✅ Car Monitor Status</b>

<b>Status:</b> Active and monitoring
<b>Last check:</b> {time_str}
<b>Listings checked:</b> {num_listings}

No new listings found in this cycle.

Still watching for perfect cars... 🔍
        """.strip()

    @staticmethod
    def _format_error(error_text, search_name=None):
        """Format error message"""

        search_info = f"\n<b>Search:</b> {search_name}" if search_name else ""

        return f"""
<b>⚠️ Car Monitor Alert</b>

<b>Issue:</b> Error during listing check{search_info}

<b>Error:</b>
<code>{error_text}</code>

Will retry in 10 minutes...
        """.strip()


def test_telegram_notifier():
    """Test the notification manager"""

    try:
        notifier = TelegramNotificationManager()

        # Test with sample car data
        sample_car = {
            "make": "Toyota",
            "model": "Land Cruiser",
            "year": 2005,
            "price": 15500,
            "currency": "USD",
            "location": "Tbilisi",
            "mileage_km": 185000,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
            "drive_type": "4WD",
            "customs_cleared": True,
            "seller_name": "John Doe",
            "posted_date": "Nov 9, 2024 10:30",
            "url": "https://www.myauto.ge/ka/pr/119084515"
        }

        logger.info("Sending test notification...")
        success = notifier.send_new_listing_notification(sample_car)

        if success:
            logger.info("[OK] Telegram notification successful!")
            return 0
        else:
            logger.error("[ERROR] Failed to send notification")
            return 1

    except Exception as e:
        logger.error(f"[ERROR] {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    exit(test_telegram_notifier())
