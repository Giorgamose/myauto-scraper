#!/usr/bin/env python3
"""
Telegram Bot Database Module - Supabase Integration
Uses existing Supabase database for storing user subscriptions
Shares same database as main monitoring system
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

try:
    from database_rest_api import DatabaseManager
except ImportError as e:
    logger.error(f"[ERROR] Failed to import DatabaseManager: {e}")
    DatabaseManager = None


class TelegramBotDatabaseSupabase:
    """Supabase database for managing user subscriptions (shared with main system)"""

    def __init__(self):
        """
        Initialize Supabase database connection using existing DatabaseManager

        Uses the same credentials as main monitoring system.
        """
        if not DatabaseManager:
            logger.error("[ERROR] DatabaseManager not available")
            raise ImportError("Failed to import DatabaseManager")

        self.db = DatabaseManager()

        if self.db.connection_failed:
            logger.error("[ERROR] Failed to connect to Supabase")
            raise ConnectionError("Supabase connection failed")

        logger.info("[OK] Telegram Bot Database initialized (Supabase)")

    def initialize_tables(self) -> bool:
        """
        Ensure required tables exist in Supabase

        Note: Tables must be created via Supabase SQL Editor.
        This method just verifies they exist.

        Required SQL to run in Supabase:
        ```sql
        -- User subscriptions (searches to monitor)
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id BIGSERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            search_url TEXT NOT NULL,
            search_name TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            last_checked TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(chat_id, search_url)
        );

        CREATE INDEX IF NOT EXISTS idx_user_subscriptions_chat_id
            ON user_subscriptions(chat_id);
        CREATE INDEX IF NOT EXISTS idx_user_subscriptions_is_active
            ON user_subscriptions(is_active);

        -- User seen listings (deduplication per user)
        CREATE TABLE IF NOT EXISTS user_seen_listings (
            id BIGSERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            listing_id TEXT NOT NULL,
            seen_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(chat_id, listing_id)
        );

        CREATE INDEX IF NOT EXISTS idx_user_seen_listings_chat_id
            ON user_seen_listings(chat_id);

        -- Bot events (logging and debugging)
        CREATE TABLE IF NOT EXISTS bot_events (
            id BIGSERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            event_type TEXT NOT NULL,
            event_data JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_bot_events_chat_id
            ON bot_events(chat_id);
        CREATE INDEX IF NOT EXISTS idx_bot_events_created_at
            ON bot_events(created_at);
        ```

        Returns:
            True if tables exist, False otherwise
        """
        try:
            # Check if tables exist by attempting to query them
            tables_to_check = [
                "user_subscriptions",
                "user_seen_listings",
                "bot_events"
            ]

            for table in tables_to_check:
                try:
                    # Try to fetch one row to verify table exists
                    response = self.db._make_request(
                        'GET',
                        f"{self.db.base_url}/{table}?limit=1",
                        headers=self.db.headers,
                        timeout=5
                    )

                    if response.status_code not in [200, 404]:
                        logger.warning(f"[WARN] Table {table} might not exist (status {response.status_code})")
                        return False

                except Exception as e:
                    logger.error(f"[ERROR] Could not verify table {table}: {e}")
                    return False

            logger.info("[OK] All required tables verified in Supabase")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize tables: {e}")
            return False

    # ========== USER SUBSCRIPTIONS ==========

    def add_subscription(self, chat_id: int, search_url: str, search_name: str = None) -> bool:
        """
        Add a new search URL subscription for a user

        If subscription already exists and is inactive, it will be re-activated.
        If subscription already exists and is active, returns False (duplicate).

        Args:
            chat_id: Telegram chat ID
            search_url: MyAuto search URL
            search_name: Optional friendly name for the search

        Returns:
            True if added or reactivated, False if already exists (and is active)
        """
        try:
            # First, check if this subscription already exists (active or inactive)
            # URL-encode the search_url since it contains special characters
            encoded_url = quote(search_url, safe='')
            filter_str = f"chat_id=eq.{chat_id}&search_url=eq.{encoded_url}"
            check_response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            existing_subs = check_response.json() if check_response.status_code == 200 else []

            if existing_subs:
                existing = existing_subs[0]
                is_active = existing.get("is_active", True)

                if is_active:
                    # Already exists and is active - this is a real duplicate
                    logger.warning(f"[!] Active subscription already exists: chat_id={chat_id}, url={search_url}")
                    return False
                else:
                    # Exists but is inactive - reactivate it
                    sub_id = existing.get("id")
                    reactivate_response = self.db._make_request(
                        'PATCH',
                        f"{self.db.base_url}/user_subscriptions?id=eq.{sub_id}",
                        json={"is_active": True, "last_checked": None},
                        headers=self.db.headers,
                        timeout=10
                    )

                    if reactivate_response.status_code in [200, 204]:
                        logger.info(f"[+] Subscription reactivated: chat_id={chat_id}, url={search_url}")
                        self._log_event(chat_id, "subscription_reactivated", {"url": search_url})
                        return True
                    else:
                        logger.error(f"[ERROR] Failed to reactivate subscription: {reactivate_response.status_code}")
                        return False

            # Subscription doesn't exist - create new one
            data = {
                "chat_id": chat_id,
                "search_url": search_url,
                "search_name": search_name or None
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/user_subscriptions",
                json=data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"[+] Subscription added: chat_id={chat_id}, url={search_url}")
                self._log_event(chat_id, "subscription_added", {"url": search_url})
                return True
            else:
                logger.error(f"[ERROR] Failed to add subscription: {response.status_code} - {response.text}")
                return False

        except Exception as e:
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
            # Filter: chat_id=<value> AND is_active=true
            filter_str = f"chat_id=eq.{chat_id}&is_active=eq.true&order=created_at.desc"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"[ERROR] Failed to get subscriptions: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get subscriptions: {e}")
            return []

    def get_all_active_subscriptions(self) -> List[Dict]:
        """
        Get all active subscriptions from all users

        Returns:
            List of all active subscriptions
        """
        try:
            # Filter: is_active=true, ordered by chat_id then created_at
            filter_str = "is_active=eq.true&order=chat_id.asc,created_at.asc"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"[ERROR] Failed to get all subscriptions: {response.status_code}")
                return []

        except Exception as e:
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
            # Update is_active to false instead of deleting
            # URL-encode the search_url since it contains special characters
            encoded_url = quote(search_url, safe='')
            filter_str = f"chat_id=eq.{chat_id}&search_url=eq.{encoded_url}"

            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                json={"is_active": False},
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[-] Subscription deleted: chat_id={chat_id}, url={search_url}")
                self._log_event(chat_id, "subscription_deleted", {"url": search_url})
                return True
            else:
                logger.warning(f"[!] Subscription not found: {response.status_code}")
                return False

        except Exception as e:
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
            # First get count of active subscriptions
            subs = self.get_subscriptions(chat_id)
            count = len(subs)

            if count == 0:
                logger.info(f"[*] No subscriptions to clear for chat_id={chat_id}")
                return 0

            # Update all to is_active=false
            filter_str = f"chat_id=eq.{chat_id}&is_active=eq.true"

            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                json={"is_active": False},
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[-] All subscriptions cleared for chat_id={chat_id} ({count} deleted)")
                self._log_event(chat_id, "subscriptions_cleared", {"count": count})
                return count
            else:
                logger.error(f"[ERROR] Failed to clear subscriptions: {response.status_code}")
                return 0

        except Exception as e:
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
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/user_subscriptions?id=eq.{subscription_id}",
                json={"last_checked": datetime.now().isoformat()},
                headers=self.db.headers,
                timeout=10
            )

            return response.status_code in [200, 204]

        except Exception as e:
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
            data = {
                "chat_id": chat_id,
                "listing_id": listing_id
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/user_seen_listings",
                json=data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return True
            elif response.status_code == 409:
                # Already seen
                return False
            else:
                logger.debug(f"[WARN] Could not mark listing seen: {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"[WARN] Failed to mark listing seen: {e}")
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
            filter_str = f"chat_id=eq.{chat_id}&listing_id=eq.{listing_id}&limit=1"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_seen_listings?{filter_str}",
                headers=self.db.headers,
                timeout=5
            )

            if response.status_code == 200:
                results = response.json()
                return len(results) > 0
            else:
                logger.debug(f"[WARN] Error checking seen listing: {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"[WARN] Failed to check if listing seen: {e}")
            return False

    def clear_subscription_seen_listings_for_ids(self, chat_id: int, listing_ids: List[str]) -> int:
        """
        Clear seen listings for a specific subscription (by listing IDs)

        Used by /reset command to clear seen status for listings in a specific search

        Args:
            chat_id: Telegram chat ID
            listing_ids: List of listing IDs to clear from seen listings

        Returns:
            Number of records cleared (approximate)
        """
        if not listing_ids:
            logger.debug("[*] No listing IDs provided to clear")
            return 0

        try:
            # Delete each listing from seen_listings for this chat
            # We need to delete multiple records, but Supabase REST API doesn't support
            # IN operator, so we delete them one by one (alternative: use raw SQL)

            deleted_count = 0
            for listing_id in listing_ids:
                try:
                    filter_str = f"chat_id=eq.{chat_id}&listing_id=eq.{listing_id}"

                    response = self.db._make_request(
                        'DELETE',
                        f"{self.db.base_url}/user_seen_listings?{filter_str}",
                        headers=self.db.headers,
                        timeout=5
                    )

                    if response.status_code in [200, 204]:
                        deleted_count += 1

                except Exception as e:
                    logger.debug(f"[WARN] Could not clear listing {listing_id}: {e}")
                    continue

            if deleted_count > 0:
                logger.info(f"[+] Cleared {deleted_count} seen listings for chat_id={chat_id}")

            return deleted_count

        except Exception as e:
            logger.error(f"[ERROR] Failed to clear subscription seen listings: {e}")
            return 0

    def cleanup_old_seen_listings(self, days: int = 30) -> int:
        """
        Clean up old seen listings (to prevent table from growing too large)

        Args:
            days: Delete seen listings older than this many days

        Returns:
            Number of records deleted (approximate)
        """
        try:
            # Calculate date threshold
            from datetime import datetime, timedelta
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Delete records older than threshold
            filter_str = f"seen_at=lt.{threshold_date}"

            response = self.db._make_request(
                'DELETE',
                f"{self.db.base_url}/user_seen_listings?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[*] Cleaned up old seen listings (>{days} days old)")
                return 1  # Supabase doesn't return count

            return 0

        except Exception as e:
            logger.debug(f"[WARN] Failed to cleanup old listings: {e}")
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
            data = {
                "chat_id": chat_id,
                "event_type": event_type,
                "event_data": event_data or {}
            }

            self.db._make_request(
                'POST',
                f"{self.db.base_url}/bot_events",
                json=data,
                headers=self.db.headers,
                timeout=5
            )

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
            if chat_id:
                filter_str = f"chat_id=eq.{chat_id}&order=created_at.desc&limit={limit}"
            else:
                filter_str = f"order=created_at.desc&limit={limit}"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/bot_events?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"[ERROR] Failed to get events: {response.status_code}")
                return []

        except Exception as e:
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
            # Get active users count
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_subscriptions?is_active=eq.true&select=chat_id",
                headers=self.db.headers,
                timeout=10
            )

            subscriptions = response.json() if response.status_code == 200 else []
            unique_chats = set(sub.get("chat_id") for sub in subscriptions)

            return {
                "total_users": len(unique_chats),
                "total_subscriptions": len(subscriptions),
                "total_seen_listings": 0,  # Would need separate query
                "database": "Supabase (shared with main system)"
            }

        except Exception as e:
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
            from datetime import datetime, timedelta
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

            filter_str = f"is_active=eq.true&last_checked=not.is.null&last_checked=lt.{threshold_date}"

            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/user_subscriptions?{filter_str}",
                json={"is_active": False},
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[*] Marked subscriptions as inactive (no checks in {days} days)")
                return 1

            return 0

        except Exception as e:
            logger.error(f"[ERROR] Failed to cleanup inactive subscriptions: {e}")
            return 0
