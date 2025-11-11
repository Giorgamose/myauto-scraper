#!/usr/bin/env python3
"""
Telegram Bot Scheduler
Periodically checks user subscriptions for new listings and sends notifications
Runs in a background thread
"""

import threading
import logging
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)


class TelegramBotScheduler(threading.Thread):
    """Background scheduler for checking user subscriptions for new listings"""

    def __init__(self, database, bot_backend, scraper, notifications_manager,
                 check_interval_minutes: int = 10, daemon: bool = True):
        """
        Initialize scheduler

        Args:
            database: TelegramBotDatabase instance
            bot_backend: TelegramBotBackend instance
            scraper: MyAutoScraper instance
            notifications_manager: NotificationManager instance
            check_interval_minutes: How often to check (in minutes)
            daemon: Run as daemon thread
        """
        super().__init__(daemon=daemon)

        self.database = database
        self.bot_backend = bot_backend
        self.scraper = scraper
        self.notifications_manager = notifications_manager

        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.running = False
        self.stats = {
            "total_checks": 0,
            "subscriptions_checked": 0,
            "new_listings_found": 0,
            "notifications_sent": 0,
            "errors": 0,
            "last_check_time": None
        }

        logger.info(f"[*] Scheduler initialized (check interval: {check_interval_minutes} minutes)")

    def run(self):
        """Main scheduler loop"""
        self.running = True
        logger.info("[*] Scheduler started")

        while self.running:
            try:
                self._execute_check_cycle()

                # Wait until next check
                logger.debug(f"[*] Next check in {self.check_interval} seconds")
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("[*] Scheduler interrupted by user")
                break

            except Exception as e:
                logger.error(f"[ERROR] Scheduler error: {e}")
                self.stats["errors"] += 1
                # Continue running even on error
                time.sleep(5)

        logger.info("[*] Scheduler stopped")
        self._log_summary()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("[*] Stopping scheduler...")

    def _execute_check_cycle(self):
        """
        Execute one complete check cycle:
        1. Get all active subscriptions
        2. Check each subscription for new listings
        3. Send notifications for new listings
        4. Update last_checked timestamp
        """
        try:
            logger.info("=" * 60)
            logger.info(f"[*] Starting check cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            cycle_start = time.time()
            self.stats["total_checks"] += 1

            # Get all active subscriptions
            subscriptions = self.database.get_all_active_subscriptions()

            if not subscriptions:
                logger.info("[*] No active subscriptions to check")
                self.stats["last_check_time"] = datetime.now()
                return

            logger.info(f"[*] Checking {len(subscriptions)} subscription(s)")

            # Group subscriptions by telegram_user_id for efficient processing
            # {telegram_user_id: {'chat_id': int, 'listings': [...]}}
            users_to_notify = {}

            for subscription in subscriptions:
                try:
                    self._check_subscription(subscription, users_to_notify)
                    self.stats["subscriptions_checked"] += 1

                except Exception as e:
                    logger.error(f"[ERROR] Error checking subscription {subscription.get('id')}: {e}")
                    self.stats["errors"] += 1
                    continue

            # Send notifications for all new listings (per user)
            for telegram_user_id, user_data in users_to_notify.items():
                try:
                    listings = user_data.get('listings', [])
                    chat_id = user_data.get('chat_id')
                    self._send_notifications_to_user(telegram_user_id, chat_id, listings)
                    self.stats["notifications_sent"] += len(listings)

                except Exception as e:
                    logger.error(f"[ERROR] Error sending notifications to user {telegram_user_id}: {e}")
                    self.stats["errors"] += 1

            # Cleanup
            self._perform_cleanup()

            # Log cycle summary
            elapsed = time.time() - cycle_start
            logger.info("=" * 60)
            logger.info(f"[*] Check cycle completed in {elapsed:.1f} seconds")
            logger.info(f"[*] Subscriptions checked: {self.stats['subscriptions_checked']}")
            logger.info(f"[*] New listings found: {self.stats['new_listings_found']}")
            logger.info(f"[*] Notifications sent: {self.stats['notifications_sent']}")
            logger.info("=" * 60)

            self.stats["last_check_time"] = datetime.now()

        except Exception as e:
            logger.error(f"[ERROR] Error in check cycle: {e}")
            self.stats["errors"] += 1

    def _check_subscription(self, subscription: Dict, users_to_notify: Dict):
        """
        Check a single subscription for new listings

        Args:
            subscription: Subscription dict with id, telegram_user_id, chat_id, search_url
            users_to_notify: Dictionary to accumulate listings per user
                           {telegram_user_id: {'chat_id': int, 'listings': [...]}}
        """
        subscription_id = subscription.get("id")
        telegram_user_id = subscription.get("telegram_user_id")
        chat_id = subscription.get("chat_id")  # Keep for notifications
        search_url = subscription.get("search_url")

        logger.debug(f"[*] Checking subscription {subscription_id}: {search_url[:60]}")

        # Fetch listings from MyAuto
        try:
            listings = self._fetch_listings_from_url(search_url)

            if not listings:
                logger.debug(f"[*] No listings found for subscription {subscription_id}")
                # Still update last_checked even if no listings found
                self.database.update_subscription_check_time(subscription_id)
                return

            logger.info(f"[+] Found {len(listings)} listings for subscription {subscription_id}")

            # Filter for new listings (not seen by this user before)
            new_listings = []

            for listing in listings:
                listing_id = listing.get("listing_id")

                if listing_id and not self.database.has_user_seen_listing(telegram_user_id, listing_id):
                    new_listings.append(listing)
                    # Mark as seen (multi-user isolation)
                    self.database.record_user_seen_listing(telegram_user_id, listing_id)
                    logger.info(f"[+] New listing found: {listing_id}")

            if new_listings:
                self.stats["new_listings_found"] += len(new_listings)

                # Accumulate listings for this telegram user
                if telegram_user_id not in users_to_notify:
                    users_to_notify[telegram_user_id] = {
                        'chat_id': chat_id,
                        'listings': []
                    }

                users_to_notify[telegram_user_id]['listings'].extend(new_listings)

            # Update last_checked timestamp
            self.database.update_subscription_check_time(subscription_id)

        except Exception as e:
            logger.error(f"[ERROR] Error checking subscription {subscription_id}: {e}")
            self.stats["errors"] += 1

    def _fetch_listings_from_url(self, search_url: str) -> List[Dict]:
        """
        Fetch listings from a MyAuto search URL

        Args:
            search_url: MyAuto.ge search URL

        Returns:
            List of listing dictionaries
        """
        if not self.scraper:
            logger.error("[ERROR] Scraper not available")
            return []

        try:
            # Create a simple search config from the URL
            search_config = {
                "base_url": search_url,
                "parameters": {}
            }

            # Fetch listings using existing scraper
            listings = self.scraper.fetch_search_results(search_config)
            return listings or []

        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch listings from {search_url}: {e}")
            return []

    def _send_notifications_to_user(self, telegram_user_id: str, chat_id: int, listings: List[Dict]):
        """
        Send notifications to a Telegram user for new listings

        Args:
            telegram_user_id: User UUID from telegram_users table
            chat_id: Telegram chat ID for sending messages
            listings: List of new listings to notify about
        """
        if not listings or not self.bot_backend:
            return

        try:
            # Check if channel notification is enabled
            notification_channel = os.getenv("TELEGRAM_NOTIFICATION_CHANNEL_ID", "").strip()

            if notification_channel:
                # Send to channel instead of individual user
                return self._send_notifications_to_channel(notification_channel, listings)

            # Send to individual user
            logger.info(f"[*] Sending {len(listings)} notification(s) to user {telegram_user_id} (chat {chat_id})")

            # Format message with listings
            if len(listings) == 1:
                message = self._format_single_listing_notification(listings[0])
            else:
                message = self._format_multiple_listings_notification(listings)

            # Send via bot
            success = self.bot_backend.send_message(chat_id, message)

            if success:
                logger.info(f"[OK] Notification sent to chat {chat_id}")
            else:
                logger.warning(f"[WARN] Failed to send notification to chat {chat_id}")

        except Exception as e:
            logger.error(f"[ERROR] Error sending notifications: {e}")

    def _send_notifications_to_channel(self, channel_id: str, listings: List[Dict]):
        """
        Send notifications to a Telegram channel instead of individual chats

        Args:
            channel_id: Telegram channel ID or username (e.g., '-1001234567890' or '@channel_name')
            listings: List of new listings to notify about
        """
        if not listings or not self.bot_backend:
            return

        try:
            logger.info(f"[*] Sending {len(listings)} notification(s) to channel {channel_id}")

            # Format message with listings
            if len(listings) == 1:
                message = self._format_single_listing_notification(listings[0])
            else:
                message = self._format_multiple_listings_notification(listings)

            # Send to channel
            success = self.bot_backend.send_message(channel_id, message)

            if success:
                logger.info(f"[OK] Notification sent to channel {channel_id}")
            else:
                logger.warning(f"[WARN] Failed to send notification to channel {channel_id}")

        except Exception as e:
            logger.error(f"[ERROR] Error sending to channel: {e}")

    @staticmethod
    def _format_single_listing_notification(listing: Dict) -> str:
        """
        Format a notification message for a single new listing

        Args:
            listing: Listing dictionary

        Returns:
            Formatted message string
        """
        # Extract fields - use title if make/model not available
        make = listing.get("make", "").strip()
        model = listing.get("model", "").strip()
        year = listing.get("year", "")
        title = listing.get("title", "").strip()

        # Build title from make/model/year if available, otherwise use title field
        if make or model:
            display_title = f"{make} {model}".strip()
            if year:
                display_title += f" ({year})"
        else:
            display_title = title if title else "New Vehicle"

        price = listing.get("price", "N/A")
        mileage = listing.get("mileage_km", "N/A")
        location = listing.get("location") or "N/A"
        fuel_type = (listing.get("fuel_type") or "").strip()
        transmission = (listing.get("transmission") or "").strip()
        url = listing.get("url") or ""

        # Format price
        if isinstance(price, (int, float)):
            price_str = f"₾{price:,.0f}"
        else:
            price_str = str(price)

        # Format mileage
        if isinstance(mileage, (int, float)):
            mileage_str = f"{mileage:,.0f} km"
        else:
            mileage_str = str(mileage)

        # Ensure URL is complete
        if url and not url.startswith("http"):
            url = f"https://www.myauto.ge{url}"

        message = f"""<b>🚗 NEW LISTING FOUND!</b>

<b>{display_title}</b>

💰 {price_str} | 📍 {location}
🛣️ {mileage_str}"""

        # Add optional fields only if available
        if fuel_type:
            message += f"\n⛽ {fuel_type}"
        if transmission:
            message += f" | 🔄 {transmission}"

        message += f"\n\n<a href=\"{url}\">View full listing →</a>"

        return message

    @staticmethod
    def _format_multiple_listings_notification(listings: List[Dict]) -> str:
        """
        Format a notification message for multiple new listings
        Uses the same format as the existing project's notifications_telegram.py

        Args:
            listings: List of listing dictionaries

        Returns:
            Formatted message string
        """
        # Use correct singular/plural form
        listing_word = "LISTING" if len(listings) == 1 else "LISTINGS"
        message = f"<b>🎉 {len(listings)} NEW CAR {listing_word}!</b>\n\n"

        for i, listing in enumerate(listings[:10], 1):  # Limit to 10 to avoid message size issues
            # Format title - use individual fields if available, otherwise use title field
            make = listing.get("make", "").strip() if listing.get("make") else ""
            model = listing.get("model", "").strip() if listing.get("model") else ""
            year = listing.get("year", "")
            title = listing.get("title", "").strip() if listing.get("title") else ""

            # Build display title
            if make or model:
                display_title = f"{make} {model}".strip()
                if year:
                    display_title += f" ({year})"
            else:
                display_title = title if title else "New Vehicle"

            # Format price with Georgian Lari symbol (₾)
            price = listing.get("price")
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
            mileage = listing.get("mileage_km")
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

            # Get optional fields with proper None handling (use empty string, not 'N/A')
            # Use (value or "") to handle both missing keys and None values
            location = (listing.get("location") or "").strip()
            fuel_type = (listing.get("fuel_type") or "").strip()
            transmission = (listing.get("transmission") or "").strip()
            url = listing.get("url") or ""

            # Ensure URL is complete
            if url and not url.startswith("http"):
                url = f"https://www.myauto.ge{url}"

            # Format the listing entry - clean compact format
            message += f"<b>{i}. {display_title}</b>\n"
            message += f"   {price_str}"
            if location:
                message += f" | 📍 {location}"
            message += f"\n   🛣️ {mileage_str} km"

            # Add optional fields only if available (not empty or N/A)
            extras = []
            if fuel_type:
                extras.append(f"⛽ {fuel_type}")
            if transmission:
                extras.append(f"🔄 {transmission}")

            if extras:
                message += f" | {' | '.join(extras)}"

            message += f"\n   <a href=\"{url}\">View listing →</a>\n\n"

        # Add info about additional listings if any
        if len(listings) > 10:
            message += f"\n<i>...and {len(listings) - 10} more listings</i>"

        return message

    def _perform_cleanup(self):
        """Perform maintenance tasks"""
        try:
            # Clean up old seen listings (keep only last 30 days)
            self.database.cleanup_old_seen_listings(days=30)

            # Mark subscriptions as inactive if not checked in 90 days
            self.database.cleanup_inactive_subscriptions(days=90)

        except Exception as e:
            logger.debug(f"[WARN] Cleanup error: {e}")

    def _log_summary(self):
        """Log scheduler statistics"""
        logger.info("[*] === SCHEDULER SUMMARY ===")
        logger.info(f"[*] Total check cycles: {self.stats['total_checks']}")
        logger.info(f"[*] Subscriptions checked: {self.stats['subscriptions_checked']}")
        logger.info(f"[*] New listings found: {self.stats['new_listings_found']}")
        logger.info(f"[*] Notifications sent: {self.stats['notifications_sent']}")
        logger.info(f"[*] Errors: {self.stats['errors']}")
        if self.stats["last_check_time"]:
            logger.info(f"[*] Last check: {self.stats['last_check_time']}")

    def get_stats(self) -> Dict:
        """
        Get current scheduler statistics

        Returns:
            Dictionary with stats
        """
        return {
            **self.stats,
            "running": self.running,
            "check_interval_minutes": self.check_interval // 60
        }
