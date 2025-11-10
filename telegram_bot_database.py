#!/usr/bin/env python3
"""
Telegram Bot Database Module
SQLite database for storing user subscriptions and tracking seen listings
"""

import sqlite3
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TelegramBotDatabase:
    """SQLite database for managing user subscriptions and seen listings"""

    def __init__(self, db_path: str = "telegram_bot.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None

        # Initialize database and schema
        self._connect()
        self._initialize_schema()

    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"[OK] Database connected: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to connect to database: {e}")
            raise

    def _initialize_schema(self):
        """Create tables if they don't exist"""
        try:
            cursor = self.connection.cursor()

            # Table: user_subscriptions
            # Stores URLs that users want to monitor
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    search_url TEXT NOT NULL,
                    search_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checked TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(chat_id, search_url)
                )
            """)

            # Table: user_seen_listings
            # Tracks listings already shown to each user to avoid duplicates
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_seen_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    listing_id TEXT NOT NULL,
                    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chat_id, listing_id)
                )
            """)

            # Table: bot_events
            # Logging of bot interactions for debugging/monitoring
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            logger.info("[OK] Database schema initialized")

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to initialize schema: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("[*] Database connection closed")

    # ========== USER SUBSCRIPTIONS ==========

    def add_subscription(self, chat_id: int, search_url: str, search_name: str = None) -> bool:
        """
        Add a new search URL subscription for a user

        Args:
            chat_id: Telegram chat ID
            search_url: MyAuto search URL
            search_name: Optional friendly name for the search

        Returns:
            True if added, False if already exists
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_subscriptions (chat_id, search_url, search_name)
                VALUES (?, ?, ?)
            """, (chat_id, search_url, search_name))
            self.connection.commit()

            logger.info(f"[+] Subscription added: chat_id={chat_id}, url={search_url}")
            self._log_event(chat_id, "subscription_added", {"url": search_url})
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"[!] Subscription already exists: chat_id={chat_id}, url={search_url}")
            return False
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to add subscription: {e}")
            return False

    def get_subscriptions(self, chat_id: int) -> List[Dict]:
        """
        Get all active subscriptions for a user

        Args:
            chat_id: Telegram chat ID

        Returns:
            List of subscription dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, chat_id, search_url, search_name, created_at, last_checked
                FROM user_subscriptions
                WHERE chat_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (chat_id,))

            rows = cursor.fetchall()
            subscriptions = [dict(row) for row in rows]
            return subscriptions

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to get subscriptions: {e}")
            return []

    def get_all_active_subscriptions(self) -> List[Dict]:
        """
        Get all active subscriptions from all users

        Returns:
            List of all active subscriptions
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, chat_id, search_url, search_name, created_at, last_checked
                FROM user_subscriptions
                WHERE is_active = 1
                ORDER BY chat_id, created_at
            """)

            rows = cursor.fetchall()
            subscriptions = [dict(row) for row in rows]
            return subscriptions

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to get all subscriptions: {e}")
            return []

    def delete_subscription(self, chat_id: int, search_url: str) -> bool:
        """
        Delete a specific subscription

        Args:
            chat_id: Telegram chat ID
            search_url: URL to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE user_subscriptions
                SET is_active = 0
                WHERE chat_id = ? AND search_url = ?
            """, (chat_id, search_url))

            self.connection.commit()

            if cursor.rowcount > 0:
                logger.info(f"[-] Subscription deleted: chat_id={chat_id}, url={search_url}")
                self._log_event(chat_id, "subscription_deleted", {"url": search_url})
                return True
            else:
                logger.warning(f"[!] Subscription not found: chat_id={chat_id}, url={search_url}")
                return False

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to delete subscription: {e}")
            return False

    def clear_subscriptions(self, chat_id: int) -> int:
        """
        Delete all subscriptions for a user

        Args:
            chat_id: Telegram chat ID

        Returns:
            Number of subscriptions deleted
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE user_subscriptions
                SET is_active = 0
                WHERE chat_id = ? AND is_active = 1
            """, (chat_id,))

            self.connection.commit()
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                logger.info(f"[-] All subscriptions cleared for chat_id={chat_id} ({deleted_count} deleted)")
                self._log_event(chat_id, "subscriptions_cleared", {"count": deleted_count})

            return deleted_count

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to clear subscriptions: {e}")
            return 0

    def update_last_checked(self, subscription_id: int) -> bool:
        """
        Update the last_checked timestamp for a subscription

        Args:
            subscription_id: Subscription ID

        Returns:
            True if updated
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE user_subscriptions
                SET last_checked = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (subscription_id,))

            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to update last_checked: {e}")
            return False

    # ========== SEEN LISTINGS ==========

    def mark_listing_seen(self, chat_id: int, listing_id: str) -> bool:
        """
        Mark a listing as seen by a user

        Args:
            chat_id: Telegram chat ID
            listing_id: MyAuto listing ID

        Returns:
            True if marked, False if already seen
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_seen_listings (chat_id, listing_id)
                VALUES (?, ?)
            """, (chat_id, listing_id))

            self.connection.commit()
            return True

        except sqlite3.IntegrityError:
            # Already seen
            return False
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to mark listing seen: {e}")
            return False

    def has_user_seen_listing(self, chat_id: int, listing_id: str) -> bool:
        """
        Check if a user has already seen a listing

        Args:
            chat_id: Telegram chat ID
            listing_id: MyAuto listing ID

        Returns:
            True if seen, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 1 FROM user_seen_listings
                WHERE chat_id = ? AND listing_id = ?
                LIMIT 1
            """, (chat_id, listing_id))

            return cursor.fetchone() is not None

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to check if listing seen: {e}")
            return False

    def cleanup_old_seen_listings(self, days: int = 30) -> int:
        """
        Clean up old seen listings (to prevent table from growing too large)

        Args:
            days: Delete seen listings older than this many days

        Returns:
            Number of records deleted
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM user_seen_listings
                WHERE seen_at < datetime('now', '-' || ? || ' days')
            """, (days,))

            self.connection.commit()
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                logger.info(f"[*] Cleaned up {deleted_count} old seen listings (>{days} days old)")

            return deleted_count

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to cleanup old listings: {e}")
            return 0

    # ========== EVENTS LOGGING ==========

    def _log_event(self, chat_id: int, event_type: str, event_data: dict = None):
        """
        Log bot interaction events for debugging

        Args:
            chat_id: Telegram chat ID
            event_type: Type of event
            event_data: Optional event data dictionary
        """
        try:
            import json
            cursor = self.connection.cursor()
            event_data_str = json.dumps(event_data) if event_data else None

            cursor.execute("""
                INSERT INTO bot_events (chat_id, event_type, event_data)
                VALUES (?, ?, ?)
            """, (chat_id, event_type, event_data_str))

            self.connection.commit()

        except Exception as e:
            logger.debug(f"[WARN] Failed to log event: {e}")

    def get_events(self, chat_id: int = None, limit: int = 100) -> List[Dict]:
        """
        Get logged events for debugging/monitoring

        Args:
            chat_id: Optional chat ID to filter by
            limit: Maximum events to retrieve

        Returns:
            List of events
        """
        try:
            cursor = self.connection.cursor()

            if chat_id:
                cursor.execute("""
                    SELECT id, chat_id, event_type, event_data, created_at
                    FROM bot_events
                    WHERE chat_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (chat_id, limit))
            else:
                cursor.execute("""
                    SELECT id, chat_id, event_type, event_data, created_at
                    FROM bot_events
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to get events: {e}")
            return []

    # ========== STATISTICS ==========

    def get_statistics(self) -> Dict:
        """
        Get bot statistics

        Returns:
            Dictionary with statistics
        """
        try:
            cursor = self.connection.cursor()

            # Total users
            cursor.execute("SELECT COUNT(DISTINCT chat_id) FROM user_subscriptions WHERE is_active = 1")
            total_users = cursor.fetchone()[0] or 0

            # Total subscriptions
            cursor.execute("SELECT COUNT(*) FROM user_subscriptions WHERE is_active = 1")
            total_subscriptions = cursor.fetchone()[0] or 0

            # Total seen listings
            cursor.execute("SELECT COUNT(*) FROM user_seen_listings")
            total_seen_listings = cursor.fetchone()[0] or 0

            return {
                "total_users": total_users,
                "total_subscriptions": total_subscriptions,
                "total_seen_listings": total_seen_listings,
                "database_file": self.db_path
            }

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to get statistics: {e}")
            return {}

    def cleanup_inactive_subscriptions(self, days: int = 90) -> int:
        """
        Mark subscriptions as inactive if not checked for N days

        Args:
            days: Number of days without check before marking inactive

        Returns:
            Number of subscriptions marked inactive
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE user_subscriptions
                SET is_active = 0
                WHERE is_active = 1 AND last_checked IS NOT NULL
                AND last_checked < datetime('now', '-' || ? || ' days')
            """, (days,))

            self.connection.commit()
            updated_count = cursor.rowcount

            if updated_count > 0:
                logger.info(f"[*] Marked {updated_count} subscriptions as inactive (no checks in {days} days)")

            return updated_count

        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to cleanup inactive subscriptions: {e}")
            return 0
