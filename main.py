#!/usr/bin/env python3
"""
Main Orchestrator Module
Complete workflow for car listing monitoring and notifications

Workflow:
1. Load configuration
2. Initialize services (database, scraper, notifications)
3. For each enabled search:
   - Fetch listings from MyAuto.ge
   - Detect new listings using deduplication
   - Send notifications for new listings
   - Update database with new data
4. Send status update
5. Cleanup old data (365+ days)
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import local modules
from utils import (
    setup_logging,
    validate_config,
    format_timestamp,
    load_config_file,
    get_enabled_searches,
    format_listing_for_display,
    calculate_statistics,
    get_config_path,
    get_log_level,
)

from database_rest_api import DatabaseManager  # Using REST API instead of direct PostgreSQL
from scraper import MyAutoScraper
from parser import MyAutoParser
from notifications import NotificationManager

logger = logging.getLogger(__name__)


class CarListingMonitor:
    """Main orchestrator for car listing monitoring workflow"""

    def __init__(self, config_path: str = None):
        """
        Initialize the monitoring system

        Args:
            config_path: Path to config.json
        """

        self.config_path = config_path or get_config_path()
        self.config = None
        self.database = None
        self.scraper = None
        self.notifier = None

        # Statistics tracking
        self.stats = {
            "searches_processed": 0,
            "total_listings_found": 0,
            "new_listings_found": 0,
            "notifications_sent": 0,
            "errors_encountered": 0,
            "start_time": datetime.now()
        }

    def initialize(self) -> bool:
        """
        Initialize all services (database, scraper, notifications)

        Returns:
            True if successful, False if failed
        """

        try:
            logger.info("[*] Initializing monitoring system...")

            # 1. Load configuration
            logger.info(f"[*] Loading config from {self.config_path}")
            self.config = load_config_file(self.config_path)

            if self.config is None:
                logger.error("[ERROR] Failed to load configuration")
                return False

            # 2. Validate configuration
            if not validate_config(self.config):
                logger.error("[ERROR] Configuration validation failed")
                return False

            # 3. Initialize database (using Supabase REST API)
            logger.info("[*] Initializing database connection...")
            try:
                self.database = DatabaseManager()
                if self.database.connection_failed:
                    logger.error("[ERROR] Failed to initialize database: connection failed")
                    return False
                if not self.database.initialize_schema():
                    logger.error("[ERROR] Failed to initialize database schema")
                    return False
                logger.info("[OK] Database initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize database: {e}")
                return False

            # 4. Initialize scraper
            logger.info("[*] Initializing scraper...")
            try:
                self.scraper = MyAutoScraper(self.config)
                logger.info("[OK] Scraper initialized")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize scraper: {e}")
                return False

            # 5. Initialize notifications
            logger.info("[*] Initializing notifications...")
            try:
                self.notifier = NotificationManager()
                if self.notifier.is_ready():
                    logger.info("[OK] Notifications initialized")
                else:
                    logger.warning("[WARN] Notifications not configured (Telegram credentials missing)")
            except Exception as e:
                logger.warning(f"[WARN] Notifications not available: {e}")

            logger.info("[OK] All services initialized successfully")

            # Initialize search configurations in database
            self._initialize_search_configs()

            return True

        except Exception as e:
            logger.error(f"[ERROR] Initialization failed: {e}")
            return False

    def _initialize_search_configs(self):
        """
        Populate search_configurations table from config.json
        """
        try:
            logger.info("[*] Initializing search configurations in database...")

            search_configs = self.config.get("search_configurations", [])

            if not search_configs:
                logger.warning("[WARN] No search configurations found in config.json")
                return

            # Use the new database method to initialize all configurations at once
            initialized_count = self.database.initialize_search_configurations(search_configs)

            if initialized_count > 0:
                logger.info(f"[OK] Initialized {initialized_count} search configuration(s)")
            else:
                logger.warning("[WARN] No new search configurations were initialized")

        except Exception as e:
            logger.warning(f"[WARN] Error initializing search configurations: {e}")

    def process_search(self, search_config: Dict) -> Tuple[List[Dict], int]:
        """
        Process a single search configuration

        Args:
            search_config: Search configuration dictionary

        Returns:
            Tuple of (new_listings, new_count)
        """

        search_id = search_config.get("id")
        search_name = search_config.get("name")
        base_url = search_config.get("base_url")

        logger.info(f"[*] Processing search: {search_name}")

        try:
            # Fetch listings from MyAuto.ge
            logger.info(f"[*] Fetching listings from {base_url}")
            listings = self.scraper.fetch_search_results(search_config)

            if not listings:
                logger.warning(f"[WARN] No listings found for {search_name}")
                return [], 0

            logger.info(f"[OK] Found {len(listings)} listings")

            # Detect new listings
            new_listings = []
            for listing in listings:
                listing_id = listing.get("listing_id")

                if listing_id and not self.database.has_seen_listing(listing_id):
                    new_listings.append(listing)
                    logger.info(f"[+] New listing: {format_listing_for_display(listing)}")

            if new_listings:
                logger.info(f"[OK] Detected {len(new_listings)} new listings")

                # Fetch detailed information for each new listing and store
                for listing in new_listings:
                    try:
                        listing_id = listing.get("listing_id")
                        logger.debug(f"[*] Fetching details for listing {listing_id}...")

                        # Fetch complete listing details
                        listing_details = self.scraper.fetch_listing_details(listing_id)

                        if listing_details:
                            # Store the complete listing data
                            self.database.store_listing(listing_details)
                            logger.info(f"[OK] Stored listing {listing_id}")
                        else:
                            # Store what we have even if details fetch failed
                            logger.warning(f"[WARN] Could not fetch details for {listing_id}, storing summary only")
                            self.database.store_listing(listing)

                    except Exception as e:
                        logger.error(f"[ERROR] Failed to store listing: {e}")
                        self.stats["errors_encountered"] += 1

            self.stats["total_listings_found"] += len(listings)
            self.stats["new_listings_found"] += len(new_listings)

            return new_listings, len(new_listings)

        except Exception as e:
            logger.error(f"[ERROR] Error processing search {search_name}: {e}")
            self.stats["errors_encountered"] += 1
            return [], 0

    def send_listing_notifications(self, new_listings: List[Dict]) -> int:
        """
        Send notifications for new listings

        Args:
            new_listings: List of new car listings

        Returns:
            Number of notifications sent
        """

        if not new_listings:
            return 0

        if not self.notifier or not self.notifier.is_ready():
            logger.warning("[WARN] Notification service not ready")
            return 0

        try:
            notification_settings = self.config.get("notification_settings", {})
            send_notifications = notification_settings.get("send_on_new_listings", True)

            if not send_notifications:
                logger.info("[*] Notifications disabled in config")
                return 0

            # Determine notification method based on count
            if len(new_listings) == 1:
                logger.info("[*] Sending single listing notification...")
                success = self.notifier.send_new_listing(new_listings[0])
                if success:
                    # Record the notification in database
                    listing_id = new_listings[0].get("listing_id")
                    if listing_id:
                        self.database.record_notification(listing_id, "telegram")
            else:
                logger.info(f"[*] Sending {len(new_listings)} listings notification...")
                success = self.notifier.send_new_listings(new_listings)
                if success:
                    # Record notifications for each listing in database
                    for listing in new_listings:
                        listing_id = listing.get("listing_id")
                        if listing_id:
                            self.database.record_notification(listing_id, "telegram")

            if success:
                logger.info("[OK] Notification sent successfully")
                return len(new_listings)
            else:
                logger.warning("[WARN] Failed to send notification")
                return 0

        except Exception as e:
            logger.error(f"[ERROR] Error sending notifications: {e}")
            return 0

    def send_status_notification(self) -> bool:
        """
        Send status/heartbeat notification

        Returns:
            True if sent successfully
        """

        notification_settings = self.config.get("notification_settings", {})
        send_heartbeat = notification_settings.get("send_heartbeat_on_no_listings", True)

        # Only send status if no new listings found
        if self.stats["new_listings_found"] > 0:
            logger.info("[*] Skipping status notification (new listings found)")
            return True

        if not send_heartbeat:
            logger.info("[*] Status notifications disabled in config")
            return True

        if not self.notifier or not self.notifier.is_ready():
            logger.info("[*] Notification service not ready for status")
            return False

        try:
            logger.info("[*] Sending status notification...")
            success = self.notifier.send_status(self.stats["total_listings_found"])
            if success:
                logger.info("[OK] Status notification sent")
            return success

        except Exception as e:
            logger.error(f"[ERROR] Error sending status notification: {e}")
            return False

    def cleanup_old_data(self) -> bool:
        """
        Clean up listings older than retention period

        Returns:
            True if successful
        """

        try:
            database_settings = self.config.get("database_settings", {})
            retention_days = database_settings.get("retention_days", 365)
            auto_cleanup = database_settings.get("auto_cleanup", True)

            if not auto_cleanup:
                logger.info("[*] Automatic cleanup disabled")
                return True

            logger.info(f"[*] Cleaning up listings older than {retention_days} days...")
            self.database.cleanup_old_listings(retention_days)
            logger.info("[OK] Cleanup completed")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Cleanup failed: {e}")
            return False

    def run_cycle(self) -> bool:
        """
        Execute complete monitoring cycle

        Workflow:
        1. Initialize services
        2. Process each enabled search
        3. Send notifications
        4. Send status update
        5. Cleanup old data

        Returns:
            True if successful
        """

        try:
            logger.info("=" * 60)
            logger.info(f"[*] Starting monitoring cycle at {format_timestamp()}")
            logger.info("=" * 60)

            # Initialize services
            if not self.initialize():
                logger.error("[ERROR] Failed to initialize services")
                return False

            # Process each enabled search
            enabled_searches = get_enabled_searches(self.config)

            for search_config in enabled_searches:
                self.stats["searches_processed"] += 1
                new_listings, new_count = self.process_search(search_config)

                # Send notifications for new listings
                if new_listings:
                    notifications_sent = self.send_listing_notifications(new_listings)
                    self.stats["notifications_sent"] += notifications_sent

            # Send status update if no new listings
            if self.stats["new_listings_found"] == 0:
                self.send_status_notification()

            # Cleanup old data
            self.cleanup_old_data()

            # Log summary statistics
            self._log_summary()

            logger.info("=" * 60)
            logger.info("[OK] Monitoring cycle completed successfully")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"[ERROR] Monitoring cycle failed: {e}")
            self.stats["errors_encountered"] += 1
            return False

    def _log_summary(self):
        """Log summary statistics for the monitoring cycle"""

        try:
            elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()

            logger.info("[*] === CYCLE SUMMARY ===")
            logger.info(f"[*] Duration: {elapsed:.1f} seconds")
            logger.info(f"[*] Searches processed: {self.stats['searches_processed']}")
            logger.info(f"[*] Total listings found: {self.stats['total_listings_found']}")
            logger.info(f"[*] New listings detected: {self.stats['new_listings_found']}")
            logger.info(f"[*] Notifications sent: {self.stats['notifications_sent']}")
            logger.info(f"[*] Errors encountered: {self.stats['errors_encountered']}")

            if self.database and self.stats["new_listings_found"] > 0:
                try:
                    db_stats = self.database.get_statistics()
                    if db_stats:
                        logger.info(f"[*] Database stats: {db_stats}")
                except Exception as e:
                    logger.warning(f"[WARN] Could not retrieve database statistics: {e}")

        except Exception as e:
            logger.error(f"[ERROR] Error logging summary: {e}")


def main():
    """Main entry point"""

    try:
        # Setup logging
        log_level = get_log_level()
        setup_logging(log_level)

        logger.info("[*] MyAuto Car Listing Monitor")
        logger.info("[*] Version: 1.0.0")

        # Create and run monitor
        monitor = CarListingMonitor()
        success = monitor.run_cycle()

        # Exit with appropriate code
        exit_code = 0 if success else 1
        logger.info(f"[*] Exiting with code {exit_code}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("[*] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
