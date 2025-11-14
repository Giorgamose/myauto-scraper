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

        # Split listings into batches to avoid exceeding Telegram's 4096 character limit
        # Each batch will be sent as a separate message
        batches = self._split_listings_into_batches(cars_list, max_listings_per_batch=10)
        all_sent = True

        for batch_num, batch in enumerate(batches, 1):
            message = self._format_multiple_listings(batch, batch_num=batch_num, total_batches=len(batches), total_listings=len(cars_list))
            if not self.send_message(message):
                all_sent = False

        return all_sent

    def send_status_notification(self, num_listings_checked=0, chat_id=None):
        """Send heartbeat/status notification

        Args:
            num_listings_checked: Number of listings checked
            chat_id: Optional chat_id to send to (defaults to self.chat_id)
        """

        message = self._format_status(num_listings_checked)

        # Use provided chat_id or default to instance chat_id
        if chat_id:
            # Temporarily override chat_id for this message
            original_chat_id = self.chat_id
            self.chat_id = chat_id
            result = self.send_message(message)
            self.chat_id = original_chat_id
            return result
        else:
            return self.send_message(message)

    def send_error_notification(self, error_text, search_name=None):
        """Send error notification"""

        message = self._format_error(error_text, search_name)
        return self.send_message(message)

    @staticmethod
    def _format_new_listing(car):
        """Format single car listing for Telegram"""

        # Format car title - use individual fields if available, otherwise use title field
        make = car.get('make', '')
        model = car.get('model', '')
        year = car.get('year', '')

        # If we have make/model/year, use them
        if make or model or year:
            title = f"{make} {model} {year}".strip()
        else:
            # Otherwise use the combined title field
            title = car.get('title', 'Unknown Vehicle')

        # Format price with Georgian Lari symbol (₾)
        price = car.get('price')
        if not price:
            price_str = 'N/A'
        elif isinstance(price, (int, float)):
            price_str = f"₾{price:,.0f}"
        else:
            # Try to parse string price
            try:
                price_num = int(str(price).replace(',', '').replace(' ', ''))
                if price_num > 100:  # Likely a real price
                    price_str = f"₾{price_num:,.0f}"
                else:
                    price_str = f"₾{price}"
            except (ValueError, AttributeError, TypeError):
                price_str = 'N/A'

        # Format mileage with thousands separator
        mileage = car.get('mileage_km', 'N/A')
        if isinstance(mileage, (int, float)):
            mileage_str = f"{mileage:,.0f} km"
        else:
            # Try to parse string mileage
            try:
                mileage_num = int(mileage.replace(',', '').replace(' ', ''))
                mileage_str = f"{mileage_num:,.0f} km"
            except (ValueError, AttributeError, TypeError):
                mileage_str = f"{mileage} km" if mileage != 'N/A' else "N/A"

        # Get optional fields with fallbacks (convert None and empty strings to 'N/A')
        location = car.get('location') or 'N/A'
        fuel_type = car.get('fuel_type') or 'N/A'
        transmission = car.get('transmission') or 'N/A'
        drive_type = car.get('drive_type') or 'N/A'
        displacement = car.get('displacement_liters') or 'N/A'
        seller_name = car.get('seller_name') or 'N/A'
        posted_date = car.get('posted_date') or 'N/A'
        description = car.get('description', '')
        url = car.get('url', '#')

        # Ensure URL is properly formatted
        if url and not url.startswith('http'):
            url = f"https://www.myauto.ge{url}"

        # Customs status indicator
        customs_status = '✅ Customs Cleared' if car.get('customs_cleared') else '⚠️ Customs Status Unknown'

        # Build base message with GEL price display
        price_display = price_str

        message = f"""
<b>🚗 NEW CAR LISTING!</b>

<b>{title}</b>

<b>💰 Price:</b> {price_display}
<b>📍 Location:</b> {location}
<b>🛣️ Mileage:</b> {mileage_str}
<b>⛽ Fuel:</b> {fuel_type}
<b>🔄 Transmission:</b> {transmission}
<b>🚙 Drive Type:</b> {drive_type}
<b>🔧 Engine:</b> {displacement} L

{customs_status}

👤 <b>Seller:</b> {seller_name}
📅 <b>Posted:</b> {posted_date}"""

        # Add description if available (limit to 500 chars)
        if description:
            # Handle dict format from scraper (e.g., {"text": "...", "features": [...]})
            if isinstance(description, dict):
                description = description.get('text', '') or description.get('description', '')

            # Ensure description is a string and not empty
            description_str = str(description).strip() if description else ''

            if description_str and len(description_str) > 0:
                description_text = description_str[:500]
                message += f"\n\n<b>Description:</b>\n{description_text}"

        message += f"\n\n<a href=\"{url}\">View full listing</a>"

        return message.strip()

    @staticmethod
    def _split_listings_into_batches(cars_list, max_listings_per_batch=10):
        """Split listings into batches to avoid exceeding Telegram's 4096 character limit

        Args:
            cars_list: List of car dictionaries
            max_listings_per_batch: Maximum listings per batch (default: 10)

        Returns:
            List of batches, where each batch is a list of car dictionaries
        """
        batches = []
        for i in range(0, len(cars_list), max_listings_per_batch):
            batches.append(cars_list[i:i + max_listings_per_batch])
        return batches

    @staticmethod
    def _format_multiple_listings(cars_list, batch_num=None, total_batches=None, total_listings=None):
        """Format multiple listings for Telegram

        Args:
            cars_list: List of car dictionaries to format
            batch_num: Current batch number (for multi-batch messages)
            total_batches: Total number of batches (for multi-batch messages)
            total_listings: Total number of listings across all batches
        """

        # Use correct singular/plural form
        listing_word = "LISTING" if len(cars_list) == 1 else "LISTINGS"

        # Add batch information if this is a multi-batch message
        if batch_num and total_batches and total_batches > 1:
            message = f"<b>🎉 {total_listings} NEW CAR LISTINGS!</b>\n<i>(Batch {batch_num} of {total_batches})</i>\n\n"
        else:
            message = f"<b>🎉 {len(cars_list)} NEW CAR {listing_word}!</b>\n\n"

        for i, car in enumerate(cars_list, 1):
            # Format title - use individual fields if available, otherwise use title field
            make = car.get('make', '')
            model = car.get('model', '')
            year = car.get('year', '')

            # If we have make/model/year, use them
            if make or model or year:
                title = f"{make} {model} {year}".strip()
            else:
                # Otherwise use the combined title field
                title = car.get('title', 'Unknown Vehicle')

            # Format price with Georgian Lari symbol (₾)
            price = car.get('price')
            if not price:
                price_str = 'N/A'
            elif isinstance(price, (int, float)):
                price_str = f"₾{price:,.0f}"
            else:
                # Try to parse string price
                try:
                    price_num = int(str(price).replace(',', '').replace(' ', ''))
                    if price_num > 100:
                        price_str = f"₾{price_num:,.0f}"
                    else:
                        price_str = f"₾{price}"
                except (ValueError, AttributeError, TypeError):
                    price_str = 'N/A'

            # Format mileage safely
            mileage = car.get('mileage_km')
            if not mileage:
                mileage_str = 'N/A'
            elif isinstance(mileage, (int, float)):
                mileage_str = f"{mileage:,.0f}"
            else:
                # Try to parse string mileage
                try:
                    mileage_num = int(str(mileage).replace(',', '').replace(' ', ''))
                    mileage_str = f"{mileage_num:,.0f}"
                except (ValueError, AttributeError, TypeError):
                    mileage_str = 'N/A'

            # Ensure URL is properly formatted
            url = car.get('url', '#')
            if url and not url.startswith('http'):
                url = f"https://www.myauto.ge{url}"

            # Get fields with proper None handling
            location = car.get('location') or 'N/A'
            fuel_type = car.get('fuel_type') or 'N/A'
            transmission = car.get('transmission') or 'N/A'
            drive_type = car.get('drive_type') or 'N/A'
            displacement = car.get('displacement_liters') or 'N/A'
            description = car.get('description', '')

            message += f"<b>{i}. {title}</b>\n"
            message += f"   {price_str} | 📍 {location}\n"
            message += f"   🛣️ {mileage_str} km | ⛽ {fuel_type}\n"
            message += f"   🔧 {displacement}L | 🚙 {drive_type} | 🔄 {transmission}\n"

            # Add description if available (limit to 150 chars for compact format)
            if description:
                # Handle dict format from scraper (e.g., {"text": "...", "features": [...]})
                if isinstance(description, dict):
                    description = description.get('text', '') or description.get('description', '')

                # Ensure description is a string and not empty
                description_str = str(description).strip() if description else ''

                if description_str and len(description_str) > 0:
                    description_short = description_str[:150]
                    if len(description_str) > 150:
                        description_short += "..."
                    message += f"   📝 {description_short}\n"

            message += f"   <a href=\"{url}\">View listing</a>\n\n"

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

        # Test with sample car data (including description)
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
            "displacement_liters": 3.0,
            "customs_cleared": True,
            "seller_name": "John Doe",
            "posted_date": "Nov 9, 2024 10:30",
            "url": "https://www.myauto.ge/ka/pr/119084515",
            "description": "Well-maintained Toyota Land Cruiser with excellent service history. Recently serviced, all fluids topped up. Interior and exterior in great condition."
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
