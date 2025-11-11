#!/usr/bin/env python3
"""
Telegram Bot Database Module - Multi-User Supabase Integration
Updated for multi-user system with proper user isolation
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

try:
    from database_rest_api import DatabaseManager
    from user_management import UserManager
except ImportError as e:
    logger.error(f"[ERROR] Failed to import modules: {e}")
    DatabaseManager = None
    UserManager = None


class TelegramBotDatabaseMultiUser:
    """
    Supabase database for multi-user system
    Handles user subscriptions with proper user isolation
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize multi-user Telegram bot database

        Args:
            db_manager: DatabaseManager instance
        """
        if db_manager:
            self.db = db_manager
        elif DatabaseManager:
            self.db = DatabaseManager()
        else:
            logger.error("[ERROR] DatabaseManager not available")
            raise ImportError("Failed to import DatabaseManager")

        if self.db.connection_failed:
            logger.error("[ERROR] Failed to connect to Supabase")
            raise ConnectionError("Supabase connection failed")

        # Initialize user manager
        self.user_manager = UserManager(self.db) if UserManager else None

        logger.info("[OK] Telegram Bot Database initialized (Multi-User)")

    # ========== USER MANAGEMENT ==========

    def get_or_create_telegram_user(self, chat_id: int, username: str = None) -> Optional[str]:
        """
        Get or create a Telegram user by chat_id

        Args:
            chat_id: Telegram chat ID
            username: Optional Telegram username

        Returns:
            User ID (UUID) if successful, None otherwise
        """
        try:
            # Try to get existing user
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_users?telegram_chat_id=eq.{chat_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                if users:
                    # User exists, return the ID
                    user_id = users[0].get("id")
                    logger.debug(f"[*] Found existing user {user_id} for chat {chat_id}")
                    return user_id

            # User doesn't exist, create new user
            import uuid
            new_user_id = str(uuid.uuid4())

            user_data = {
                "id": new_user_id,
                "telegram_chat_id": chat_id,
                "telegram_username": username,
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/telegram_users",
                json=user_data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"[+] Created new Telegram user {new_user_id} for chat {chat_id}")
                return new_user_id
            else:
                logger.error(f"[ERROR] Failed to create user: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Failed to get or create user: {e}")
            return None

    # ========== SUBSCRIPTION MANAGEMENT ==========

    def add_subscription(
        self,
        user_id: str,
        search_url: str,
        search_name: str = None,
        search_criteria_id: str = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Add a new search URL subscription for a user

        Args:
            user_id: User ID (UUID from users table)
            search_url: MyAuto search URL
            search_name: Optional friendly name for the search
            search_criteria_id: Optional reference to user_search_criteria

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Count current subscriptions
            current_subs = self._count_active_subscriptions(user_id)
            max_subs = 50  # Default limit for subscriptions per user
            if current_subs >= max_subs:
                return False, f"Subscription limit reached ({max_subs})"

            # Check for duplicate subscription
            existing = self._get_subscription(user_id, search_url)
            if existing:
                if existing.get("is_active"):
                    return False, "Subscription already exists"
                else:
                    # Reactivate inactive subscription
                    return self._reactivate_subscription(existing.get("id"))

            # Create new subscription
            data = {
                "user_id": user_id,
                "search_url": search_url,
                "search_name": search_name or None,
                "search_criteria_id": search_criteria_id or None,
                "is_active": True
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/telegram_user_subscriptions",
                json=data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to add subscription: {response.status_code}")
                return False, "Failed to add subscription"

            # Log event
            self._log_event(user_id, "subscription_added", {
                "search_url": search_url,
                "search_name": search_name
            })

            logger.info(f"[+] Subscription added for user {user_id}: {search_name or search_url}")
            return True, None

        except Exception as e:
            logger.error(f"[ERROR] Failed to add subscription: {e}")
            return False, str(e)

    def get_subscriptions(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """
        Get all subscriptions for a user

        Args:
            user_id: User ID
            active_only: Only return active subscriptions

        Returns:
            List of subscription dictionaries
        """
        try:
            filter_str = f"user_id=eq.{user_id}"
            if active_only:
                filter_str += "&is_active=eq.true"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_subscriptions?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get subscriptions: {e}")
            return []

    def delete_subscription(self, user_id: str, subscription_id: str, soft_delete: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Delete a subscription (soft or hard delete)

        Args:
            user_id: User ID (for authorization check)
            subscription_id: Subscription ID
            soft_delete: If True, mark as inactive. If False, hard delete.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Verify ownership
            sub = self._get_subscription_by_id(subscription_id)
            if not sub or sub.get("user_id") != user_id:
                return False, "Subscription not found or unauthorized"

            if soft_delete:
                # Mark as inactive
                response = self.db._make_request(
                    'PATCH',
                    f"{self.db.base_url}/telegram_user_subscriptions?id=eq.{subscription_id}",
                    json={"is_active": False},
                    headers=self.db.headers,
                    timeout=10
                )
            else:
                # Hard delete
                response = self.db._make_request(
                    'DELETE',
                    f"{self.db.base_url}/telegram_user_subscriptions?id=eq.{subscription_id}",
                    headers=self.db.headers,
                    timeout=10
                )

            if response.status_code in [200, 204]:
                self._log_event(user_id, "subscription_deleted", {
                    "subscription_id": subscription_id
                })
                logger.info(f"[+] Subscription deleted: {subscription_id}")
                return True, None
            else:
                return False, "Delete failed"

        except Exception as e:
            logger.error(f"[ERROR] Failed to delete subscription: {e}")
            return False, str(e)

    def clear_subscriptions(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Clear all subscriptions for a user

        Args:
            user_id: User ID

        Returns:
            Tuple of (success, error_message)
        """
        try:
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_user_subscriptions?user_id=eq.{user_id}",
                json={"is_active": False},
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                self._log_event(user_id, "all_subscriptions_cleared", {})
                logger.info(f"[+] All subscriptions cleared for user {user_id}")
                return True, None
            else:
                return False, "Clear failed"

        except Exception as e:
            logger.error(f"[ERROR] Failed to clear subscriptions: {e}")
            return False, str(e)

    # ========== DEDUPLICATION (Seen Listings) ==========

    def record_user_seen_listing(self, user_id: str, listing_id: str) -> bool:
        """
        Record that a user has seen a listing (deduplication)

        Args:
            user_id: User ID
            listing_id: MyAuto listing ID

        Returns:
            True if recorded, False otherwise
        """
        try:
            data = {
                "user_id": user_id,
                "listing_id": listing_id
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/telegram_user_seen_listings",
                json=data,
                headers={**self.db.headers, "Prefer": "resolution=ignore-duplicates"},
                timeout=10
            )

            return response.status_code in [200, 201]

        except Exception as e:
            logger.error(f"[ERROR] Failed to record seen listing: {e}")
            return False

    def get_user_seen_listings(self, user_id: str) -> List[str]:
        """
        Get all listing IDs seen by a user

        Args:
            user_id: User ID

        Returns:
            List of listing IDs
        """
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_seen_listings?user_id=eq.{user_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                listings = response.json()
                return [item.get("listing_id") for item in listings]
            return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get seen listings: {e}")
            return []

    def has_user_seen_listing(self, user_id: str, listing_id: str) -> bool:
        """
        Check if user has seen a listing

        Args:
            user_id: User ID
            listing_id: Listing ID

        Returns:
            True if user has seen listing, False otherwise
        """
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_seen_listings?user_id=eq.{user_id}&listing_id=eq.{listing_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return len(response.json()) > 0
            return False

        except Exception as e:
            logger.error(f"[ERROR] Failed to check seen listing: {e}")
            return False

    # ========== EVENT LOGGING ==========

    def log_event(self, user_id: str, event_type: str, event_data: Dict = None) -> bool:
        """
        Log a bot event for user

        Args:
            user_id: User ID
            event_type: Type of event
            event_data: Optional event data

        Returns:
            True if logged, False otherwise
        """
        return self._log_event(user_id, event_type, event_data or {})

    def _log_event(self, user_id: str, event_type: str, event_data: Dict = None) -> bool:
        """Internal event logging"""
        try:
            data = {
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data or {}
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/telegram_bot_events",
                json=data,
                headers=self.db.headers,
                timeout=10
            )

            return response.status_code in [200, 201]

        except Exception as e:
            logger.error(f"[ERROR] Failed to log event: {e}")
            return False

    def get_user_events(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get recent events for user

        Args:
            user_id: User ID
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_bot_events?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get events: {e}")
            return []

    # ========== GET ALL ACTIVE SUBSCRIPTIONS ==========

    def get_all_active_subscriptions(self) -> List[Dict]:
        """
        Get all active subscriptions across all users (for scheduler)

        Returns:
            List of subscription dictionaries with user info
        """
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_subscriptions?is_active=eq.true&select=*,users(id,username,telegram_chat_id,check_interval_minutes)",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get all subscriptions: {e}")
            return []

    def update_subscription_check_time(self, subscription_id: str) -> bool:
        """
        Update last_checked timestamp for a subscription

        Args:
            subscription_id: Subscription ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_user_subscriptions?id=eq.{subscription_id}",
                json={"last_checked": datetime.now().isoformat()},
                headers=self.db.headers,
                timeout=10
            )

            return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"[ERROR] Failed to update check time: {e}")
            return False

    # ========== HELPERS ==========

    def _get_subscription(self, user_id: str, search_url: str) -> Optional[Dict]:
        """Get subscription by user_id and search_url"""
        try:
            encoded_url = quote(search_url, safe='')
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_subscriptions?user_id=eq.{user_id}&search_url=eq.{encoded_url}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                subs = response.json()
                return subs[0] if subs else None
            return None

        except Exception as e:
            logger.error(f"[ERROR] Failed to get subscription: {e}")
            return None

    def _get_subscription_by_id(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription by ID"""
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_subscriptions?id=eq.{subscription_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                subs = response.json()
                return subs[0] if subs else None
            return None

        except Exception as e:
            logger.error(f"[ERROR] Failed to get subscription: {e}")
            return None

    def _reactivate_subscription(self, subscription_id: str) -> Tuple[bool, Optional[str]]:
        """Reactivate an inactive subscription"""
        try:
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_user_subscriptions?id=eq.{subscription_id}",
                json={"is_active": True, "last_checked": None},
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[+] Subscription reactivated: {subscription_id}")
                return True, None
            else:
                return False, "Reactivation failed"

        except Exception as e:
            logger.error(f"[ERROR] Failed to reactivate subscription: {e}")
            return False, str(e)

    def _count_active_subscriptions(self, user_id: str) -> int:
        """Count active subscriptions for user"""
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/telegram_user_subscriptions?user_id=eq.{user_id}&is_active=eq.true&select=id",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return len(response.json())
            return 0

        except Exception as e:
            logger.error(f"[ERROR] Failed to count subscriptions: {e}")
            return 0

    def mark_listing_seen(self, user_id: str, listing_id: str) -> bool:
        """
        Mark a listing as seen by a user (alias for record_user_seen_listing)

        Args:
            user_id: User ID
            listing_id: MyAuto listing ID

        Returns:
            True if marked, False otherwise
        """
        return self.record_user_seen_listing(user_id, listing_id)

    def clear_subscription_seen_listings_for_ids(self, user_id: str, listing_ids: List[str]) -> int:
        """
        Clear seen listings for specific listing IDs

        Args:
            user_id: User ID
            listing_ids: List of listing IDs to clear

        Returns:
            Number of listings cleared
        """
        try:
            cleared_count = 0

            for listing_id in listing_ids:
                try:
                    response = self.db._make_request(
                        'DELETE',
                        f"{self.db.base_url}/telegram_user_seen_listings?user_id=eq.{user_id}&listing_id=eq.{listing_id}",
                        headers=self.db.headers,
                        timeout=10
                    )

                    if response.status_code in [200, 204]:
                        cleared_count += 1

                except Exception as e:
                    logger.debug(f"[WARN] Failed to clear listing {listing_id}: {e}")
                    continue

            return cleared_count

        except Exception as e:
            logger.error(f"[ERROR] Failed to clear listings: {e}")
            return 0

    def update_last_checked(self, subscription_id: str) -> bool:
        """
        Update the last_checked timestamp for a subscription (alias for update_subscription_check_time)

        Args:
            subscription_id: Subscription ID

        Returns:
            True if updated, False otherwise
        """
        return self.update_subscription_check_time(subscription_id)


# ============================================================================
# Migration Helper: Convert from chat_id to user_id
# ============================================================================

class MigrationHelper:
    """Helper to migrate from chat_id-based system to user_id system"""

    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize migration helper"""
        if db_manager:
            self.db = db_manager
        elif DatabaseManager:
            self.db = DatabaseManager()
        else:
            raise ImportError("Failed to import DatabaseManager")

    def migrate_chat_id_to_user_id(self, chat_id: int, user_id: str) -> bool:
        """
        Migrate a user from chat_id-based system to user_id

        This updates all old records to have the new user_id while keeping
        chat_id for legacy reference.

        Args:
            chat_id: Old Telegram chat ID
            user_id: New user UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[*] Migrating chat_id {chat_id} to user_id {user_id}")

            # Update subscriptions
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_user_subscriptions_old?chat_id=eq.{chat_id}",
                json={"user_id": user_id, "chat_id": chat_id},  # Keep for reference
                headers=self.db.headers,
                timeout=10
            )

            # Update seen listings
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_user_seen_listings_old?chat_id=eq.{chat_id}",
                json={"user_id": user_id, "chat_id": chat_id},
                headers=self.db.headers,
                timeout=10
            )

            # Update bot events
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/telegram_bot_events_old?chat_id=eq.{chat_id}",
                json={"user_id": user_id, "chat_id": chat_id},
                headers=self.db.headers,
                timeout=10
            )

            logger.info(f"[+] Migration completed for chat_id {chat_id}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Migration failed: {e}")
            return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("[*] Telegram Bot Database Multi-User module loaded")
