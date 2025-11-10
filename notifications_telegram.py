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

        # Format price with thousands separator
        price = car.get('price')
        if not price:
            price_str = 'N/A'
        elif isinstance(price, (int, float)):
            price_str = f"${price:,.0f}"
        else:
            # Try to parse string price
            try:
                price_num = int(str(price).replace(',', '').replace(' ', ''))
                if price_num > 100:  # Likely a real price
                    price_str = f"${price_num:,.0f}"
                else:
                    price_str = f"${price}"
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

        # Build base message with price display (support both USD and GEL)
        currency = car.get('currency', 'USD')
        price_display = f"{price_str} {currency}" if price_str != 'N/A' else price_str

        # Add both USD and GEL prices if available
        price_usd = car.get('price_usd')
        price_gel = car.get('price_gel')

        if price_usd and price_gel:
            try:
                usd_val = int(str(price_usd).replace(',', '').replace(' ', ''))
                gel_val = int(str(price_gel).replace(',', '').replace(' ', ''))
                price_display = f"💵 ${usd_val:,} USD | 💎 ₾{gel_val:,} GEL"
            except (ValueError, AttributeError, TypeError):
                pass  # Fall back to original price_display

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
            if isinstance(description, dict):
                description = description.get('text', '')
            if description:
                description_text = str(description)[:500]
                message += f"\n\n<b>Description:</b>\n{description_text}"

        message += f"\n\n<a href=\"{url}\">View full listing</a>"

        return message.strip()

    @staticmethod
    def _format_multiple_listings(cars_list):
        """Format multiple listings for Telegram"""

        # Use correct singular/plural form
        listing_word = "LISTING" if len(cars_list) == 1 else "LISTINGS"
        message = f"<b>🎉 {len(cars_list)} NEW CAR {listing_word}!</b>\n\n"

        for i, car in enumerate(cars_list[:10], 1):
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

            # Format price safely (support both USD and GEL)
            price = car.get('price')
            price_usd = car.get('price_usd')
            price_gel = car.get('price_gel')

            if price_usd and price_gel:
                try:
                    usd_val = int(str(price_usd).replace(',', '').replace(' ', ''))
                    gel_val = int(str(price_gel).replace(',', '').replace(' ', ''))
                    price_str = f"💵 ${usd_val:,} | 💎 ₾{gel_val:,}"
                except (ValueError, AttributeError, TypeError):
                    # Fall back to single price
                    if not price:
                        price_str = 'N/A'
                    elif isinstance(price, (int, float)):
                        price_str = f"${price:,.0f}"
                    else:
                        try:
                            price_num = int(str(price).replace(',', '').replace(' ', ''))
                            price_str = f"${price_num:,.0f}" if price_num > 100 else f"${price}"
                        except (ValueError, AttributeError, TypeError):
                            price_str = 'N/A'
            elif not price:
                price_str = 'N/A'
            elif isinstance(price, (int, float)):
                price_str = f"${price:,.0f}"
            else:
                # Try to parse string price
                try:
                    price_num = int(str(price).replace(',', '').replace(' ', ''))
                    if price_num > 100:
                        price_str = f"${price_num:,.0f}"
                    else:
                        price_str = f"${price}"
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
                if isinstance(description, dict):
                    description = description.get('text', '')
                if description:
                    description_short = str(description)[:150]
                    if len(str(description)) > 150:
                        description_short += "..."
                    message += f"   📝 {description_short}\n"

            message += f"   <a href=\"{url}\">View listing</a>\n\n"

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
