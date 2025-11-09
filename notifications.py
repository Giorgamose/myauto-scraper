#!/usr/bin/env python3
"""
Notifications Module - Telegram Integration
Wrapper around notifications_telegram.py for easy notification sending
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional

try:
    from notifications_telegram import TelegramNotificationManager
except ImportError:
    TelegramNotificationManager = None

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manage all notifications for the scraper"""

    def __init__(self):
        """Initialize notification manager"""

        try:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")

            if not bot_token or not chat_id:
                logger.error("[ERROR] Missing Telegram credentials")
                raise ValueError("Telegram bot token and chat ID required")

            if not TelegramNotificationManager:
                raise ImportError("notifications_telegram module not found")

            self.telegram = TelegramNotificationManager()
            logger.info("[OK] Notification manager initialized")

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize notifications: {e}")
            self.telegram = None

    def is_ready(self) -> bool:
        """Check if notification service is ready"""

        return self.telegram is not None

    def send_new_listing(self, car_data: Dict) -> bool:
        """
        Send notification for a single new listing

        Args:
            car_data: Dictionary with car details

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        try:
            logger.info(f"[*] Sending notification for listing: {car_data.get('listing_id')}")

            success = self.telegram.send_new_listing_notification(car_data)

            if success:
                logger.info("[OK] Notification sent successfully")
            else:
                logger.warning("[WARN] Failed to send notification")

            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending notification: {e}")
            return False

    def send_new_listings(self, cars_list: List[Dict]) -> bool:
        """
        Send notification for multiple new listings

        Args:
            cars_list: List of car data dictionaries

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        if not cars_list:
            logger.warning("[WARN] Empty cars list")
            return False

        try:
            logger.info(f"[*] Sending notification for {len(cars_list)} listings")

            success = self.telegram.send_new_listings_notification(cars_list)

            if success:
                logger.info("[OK] Notification sent successfully")
            else:
                logger.warning("[WARN] Failed to send notification")

            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending notifications: {e}")
            return False

    def send_status(self, num_checked: int = 0, status: str = "active") -> bool:
        """
        Send status/heartbeat notification

        Args:
            num_checked: Number of listings checked
            status: Status message (active, paused, etc)

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        try:
            logger.info("[*] Sending status notification")

            success = self.telegram.send_status_notification(num_checked)

            if success:
                logger.info("[OK] Status notification sent")
            else:
                logger.warning("[WARN] Failed to send status notification")

            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending status: {e}")
            return False

    def send_error(self, error_text: str, search_name: str = None) -> bool:
        """
        Send error notification

        Args:
            error_text: Error description
            search_name: Name of search that failed (optional)

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        try:
            logger.warning(f"[*] Sending error notification: {error_text}")

            success = self.telegram.send_error_notification(error_text, search_name)

            if success:
                logger.info("[OK] Error notification sent")
            else:
                logger.warning("[WARN] Failed to send error notification")

            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending error notification: {e}")
            return False

    def send_raw_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send raw message (advanced usage)

        Args:
            message: Message text (supports HTML formatting)
            parse_mode: "HTML" or "Markdown"

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        try:
            success = self.telegram.send_message(message, parse_mode=parse_mode)
            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending raw message: {e}")
            return False

    def send_formatted_listing(self, car_data: Dict, include_image: bool = False) -> bool:
        """
        Send formatted listing with optional image

        Args:
            car_data: Car data dictionary
            include_image: Whether to include primary image

        Returns:
            True if successful
        """

        if not self.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return False

        try:
            # If image available and requested, send as photo
            if include_image and car_data.get("media", {}).get("primary_image_url"):
                image_url = car_data["media"]["primary_image_url"]

                # Format caption
                caption = self._format_listing_caption(car_data)

                success = self.telegram.send_photo(image_url, caption=caption)

            else:
                # Send as text
                success = self.send_new_listing(car_data)

            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending formatted listing: {e}")
            return False

    @staticmethod
    def _format_listing_caption(car_data: Dict) -> str:
        """Format car data as caption for photo"""

        vehicle = car_data.get("vehicle", {})
        pricing = car_data.get("pricing", {})
        condition = car_data.get("condition", {})
        seller = car_data.get("seller", {})

        caption = f"""
<b>{vehicle.get('make', 'Unknown')} {vehicle.get('model', '')} {vehicle.get('year', '')}</b>

💰 <b>Price:</b> ${pricing.get('price', 'N/A'):,} {pricing.get('currency', 'USD')}
📍 <b>Location:</b> {seller.get('location', 'N/A')}
🛣️ <b>Mileage:</b> {condition.get('mileage_km', 'N/A'):,} km

<a href="{car_data.get('url', '#')}">View full listing</a>
        """.strip()

        return caption


def test_notifications():
    """Test notification system"""

    logging.basicConfig(level=logging.INFO)

    logger.info("[*] Testing notifications...")

    notifier = NotificationManager()

    if not notifier.is_ready():
        logger.error("[ERROR] Notification service not ready")
        logger.info("    Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set")
        return False

    logger.info("[OK] Notification service is ready")

    # Test status notification
    logger.info("[*] Sending test status notification...")
    success = notifier.send_status(num_checked=5)

    if success:
        logger.info("[OK] Status notification sent successfully!")
        return True
    else:
        logger.error("[ERROR] Failed to send status notification")
        return False


if __name__ == "__main__":
    import sys
    exit(0 if test_notifications() else 1)
