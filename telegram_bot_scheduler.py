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
from notifications_telegram import TelegramNotificationManager

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

# Import scraper for creating instance in scheduler thread
try:
    from scraper import MyAutoScraper
except ImportError:
    logger.warning("[WARN] Failed to import scraper module")


class TelegramBotScheduler(threading.Thread):
    """Background scheduler for checking user subscriptions for new listings"""

    def __init__(self, database, bot_backend, config, notifications_manager,
                 check_interval_minutes: int = 10, daemon: bool = True):
        """
        Initialize scheduler

        Args:
            database: TelegramBotDatabase instance
            bot_backend: TelegramBotBackend instance
            config: Configuration dictionary (used to create scraper in scheduler thread)
            notifications_manager: NotificationManager instance
            check_interval_minutes: How often to check (in minutes)
            daemon: Run as daemon thread
        """
        super().__init__(daemon=daemon)

        self.database = database
        self.bot_backend = bot_backend
        self.config = config  # Store config for creating scraper in thread
        self.scraper = None  # Will be created in run() method (thread-safe)
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

        # Create scraper instance in this thread (thread-safe)
        # This ensures the Playwright browser is tied to the scheduler thread
        try:
            if self.config:
                self.scraper = MyAutoScraper(self.config)
                logger.info("[OK] Scraper created in scheduler thread (thread-safe)")
            else:
                logger.error("[ERROR] Configuration not available for scraper initialization")
        except Exception as e:
            logger.error(f"[WARN] Failed to initialize scraper in scheduler thread: {e}")
            logger.info("[*] Scheduler will continue but listing enrichment will be disabled")
            self.scraper = None

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

    def _enrich_listings_with_details(self, listings: List[Dict]) -> List[Dict]:
        """
        Enrich basic listing summaries with detailed information
        Fetches full details for each listing to include fuel type, transmission, etc.
        Properly flattens nested detailed data structure for formatter compatibility.

        Args:
            listings: List of basic listing summaries

        Returns:
            List of enriched listing dictionaries with flat structure
        """
        enriched = []

        for listing in listings:
            listing_id = listing.get("listing_id")

            if listing_id:
                try:
                    # Fetch detailed information for this listing
                    detailed = self.scraper.fetch_listing_details(listing_id)
                    if detailed:
                        # Flatten the nested structure from scraper into flat keys for formatter
                        flattened = self._flatten_listing_details(detailed)

                        # Log what we're enriching with
                        if flattened:
                            fields_found = [k for k in ['fuel_type', 'transmission', 'drive_type', 'location', 'displacement_liters'] if k in flattened and flattened[k]]
                            logger.debug(f"[OK] Enriched listing {listing_id} with: {fields_found}")

                        # Merge flattened details with summary, detailed info takes priority
                        listing.update(flattened)
                        enriched.append(listing)
                    else:
                        # Use summary if details fetch fails
                        logger.debug(f"[WARN] No detailed data fetched for listing {listing_id}, using summary only")
                        enriched.append(listing)
                except Exception as e:
                    logger.warning(f"[WARN] Could not fetch details for listing {listing_id}: {e}")
                    enriched.append(listing)
            else:
                enriched.append(listing)

        return enriched

    def _flatten_listing_details(self, detailed: Dict) -> Dict:
        """
        Flatten nested listing detail structure into flat keys for formatter

        The scraper returns: {
            "vehicle": {"make": ..., "model": ..., "year": ...},
            "engine": {"fuel_type": ..., "displacement_liters": ..., "transmission": ...},
            "condition": {"mileage_km": ..., "customs_cleared": ...},
            "pricing": {"price": ..., "currency": ...},
            "seller": {"location": ..., "seller_name": ...}
        }

        This method flattens it to: {
            "make": ..., "model": ..., "year": ...,
            "fuel_type": ..., "displacement_liters": ..., "transmission": ...,
            "mileage_km": ..., "customs_cleared": ...,
            "price": ..., "currency": ...,
            "location": ..., "seller_name": ...
        }

        Args:
            detailed: Nested detailed listing dictionary

        Returns:
            Flattened dictionary with all keys at top level
        """
        flattened = {}

        # Extract vehicle info
        vehicle = detailed.get("vehicle", {})
        if vehicle:
            for key in ['make', 'model', 'year', 'color', 'body_type', 'category',
                       'interior_color', 'interior_material', 'wheel_position', 'doors', 'seats']:
                if key in vehicle and vehicle[key]:
                    flattened[key] = vehicle[key]

        # Extract engine info
        engine = detailed.get("engine", {})
        if engine:
            for key in ['fuel_type', 'displacement_liters', 'cylinders', 'transmission',
                       'power_hp', 'drive_type']:
                if key in engine and engine[key]:
                    flattened[key] = engine[key]

        # Extract condition/mileage info
        condition = detailed.get("condition", {})
        if condition:
            for key in ['mileage_km', 'mileage_unit', 'customs_cleared', 'technical_inspection_passed',
                       'has_catalytic_converter']:
                if key in condition and condition[key] is not None:
                    flattened[key] = condition[key]

        # Extract pricing info
        pricing = detailed.get("pricing", {})
        if pricing:
            for key in ['price', 'currency', 'currency_id', 'exchange_possible', 'negotiable',
                       'installment_available']:
                if key in pricing and pricing[key] is not None:
                    flattened[key] = pricing[key]

        # Extract seller info
        seller = detailed.get("seller", {})
        if seller:
            for key in ['seller_name', 'location', 'phone', 'email', 'seller_type']:
                if key in seller and seller[key]:
                    flattened[key] = seller[key]

        # Extract top-level fields that might not be nested
        for key in ['url', 'listing_id', 'posted_date', 'last_updated', 'description', 'photos']:
            if key in detailed and detailed[key] is not None:
                flattened[key] = detailed[key]

        return flattened

    def _send_notifications_to_user(self, telegram_user_id: str, chat_id: int, listings: List[Dict]):
        """
        Send notifications to a Telegram user for new listings
        Uses the same batching logic as notifications_telegram.py

        Args:
            telegram_user_id: User UUID from telegram_users table
            chat_id: Telegram chat ID for sending messages
            listings: List of new listings to notify about
        """
        if not listings or not self.bot_backend:
            return

        try:
            # Enrich listings with detailed information
            enriched_listings = self._enrich_listings_with_details(listings)

            # Check if channel notification is enabled
            notification_channel = os.getenv("TELEGRAM_NOTIFICATION_CHANNEL_ID", "").strip()

            if notification_channel:
                # Send to channel instead of individual user
                return self._send_notifications_to_channel(notification_channel, enriched_listings)

            # Send to individual user
            logger.info(f"[*] Sending {len(enriched_listings)} notification(s) to user {telegram_user_id} (chat {chat_id})")

            # Handle single listing
            if len(enriched_listings) == 1:
                message = self._format_single_listing_notification(enriched_listings[0])
                success = self.bot_backend.send_message(chat_id, message)

                if success:
                    logger.info(f"[OK] Notification sent to chat {chat_id}")
                else:
                    logger.warning(f"[WARN] Failed to send notification to chat {chat_id}")
            else:
                # Handle multiple listings with batching (same as notifications_telegram.py)
                batches = TelegramNotificationManager._split_listings_into_batches(enriched_listings, max_listings_per_batch=10)

                for batch_num, batch in enumerate(batches, 1):
                    # Format with batch info if multi-batch
                    if len(batches) > 1:
                        message = TelegramNotificationManager._format_multiple_listings(
                            batch,
                            batch_num=batch_num,
                            total_batches=len(batches),
                            total_listings=len(enriched_listings)
                        )
                    else:
                        message = self._format_multiple_listings_notification(batch)

                    success = self.bot_backend.send_message(chat_id, message)

                    if success:
                        logger.info(f"[OK] Batch {batch_num}/{len(batches)} sent to chat {chat_id}")
                    else:
                        logger.warning(f"[WARN] Failed to send batch {batch_num}/{len(batches)} to chat {chat_id}")

                    # Add small delay between messages to ensure they're all delivered
                    if batch_num < len(batches):
                        time.sleep(1)

        except Exception as e:
            logger.error(f"[ERROR] Error sending notifications: {e}")

    def _send_notifications_to_channel(self, channel_id: str, listings: List[Dict]):
        """
        Send notifications to a Telegram channel instead of individual chats
        Uses the same batching logic as notifications_telegram.py

        Args:
            channel_id: Telegram channel ID or username (e.g., '-1001234567890' or '@channel_name')
            listings: List of new listings to notify about
        """
        if not listings or not self.bot_backend:
            return

        try:
            logger.info(f"[*] Sending {len(listings)} notification(s) to channel {channel_id}")

            # Handle single listing
            if len(listings) == 1:
                message = self._format_single_listing_notification(listings[0])
                success = self.bot_backend.send_message(channel_id, message)

                if success:
                    logger.info(f"[OK] Notification sent to channel {channel_id}")
                else:
                    logger.warning(f"[WARN] Failed to send notification to channel {channel_id}")
            else:
                # Handle multiple listings with batching (same as notifications_telegram.py)
                batches = TelegramNotificationManager._split_listings_into_batches(listings, max_listings_per_batch=10)

                for batch_num, batch in enumerate(batches, 1):
                    # Format with batch info if multi-batch
                    if len(batches) > 1:
                        message = TelegramNotificationManager._format_multiple_listings(
                            batch,
                            batch_num=batch_num,
                            total_batches=len(batches),
                            total_listings=len(listings)
                        )
                    else:
                        message = self._format_multiple_listings_notification(batch)

                    success = self.bot_backend.send_message(channel_id, message)

                    if success:
                        logger.info(f"[OK] Batch {batch_num}/{len(batches)} sent to channel {channel_id}")
                    else:
                        logger.warning(f"[WARN] Failed to send batch {batch_num}/{len(batches)} to channel {channel_id}")

                    # Add small delay between messages to ensure they're all delivered
                    if batch_num < len(batches):
                        time.sleep(1)

        except Exception as e:
            logger.error(f"[ERROR] Error sending to channel: {e}")

    @staticmethod
    def _format_single_listing_notification(listing: Dict) -> str:
        """
        Format a notification message for a single new listing
        Uses the exact same formatting as notifications_telegram.py

        Args:
            listing: Listing dictionary

        Returns:
            Formatted message string
        """
        return TelegramNotificationManager._format_new_listing(listing)

    @staticmethod
    def _format_multiple_listings_notification(listings: List[Dict]) -> str:
        """
        Format a notification message for multiple new listings
        Uses the exact same formatting as notifications_telegram.py

        Args:
            listings: List of listing dictionaries

        Returns:
            Formatted message string
        """
        return TelegramNotificationManager._format_multiple_listings(listings)

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
