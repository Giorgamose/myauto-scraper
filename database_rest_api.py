#!/usr/bin/env python3
"""
Database Manager - Supabase REST API Operations
Handles all database interactions using Supabase REST API (no direct PostgreSQL)
This avoids IPv6 connectivity issues that occur with direct connections in GitHub Actions
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import json
from dotenv import load_dotenv

# Suppress SSL warnings when verification is disabled
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env files
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception as e:
    logger.warning(f"[WARN] Could not import requests: {e}")
    REQUESTS_AVAILABLE = False


class DatabaseManager:
    """Manage Supabase database operations using REST API instead of direct PostgreSQL"""

    # Flag to track if SSL verification should be disabled
    _ssl_verify = True

    def __init__(self, project_url: str = None, api_key: str = None):
        """
        Initialize Supabase REST API database connection

        Args:
            project_url: Supabase project URL (e.g., https://xxxxx.supabase.co)
            api_key: Supabase API key (use SUPABASE_API_KEY environment variable)
        """
        self.project_url = project_url or os.getenv("SUPABASE_URL")
        self.api_key = api_key or os.getenv("SUPABASE_API_KEY")
        self.connection_failed = False

        if not REQUESTS_AVAILABLE:
            logger.error("[ERROR] requests library not available - install: pip install requests")
            self.connection_failed = True
            return

        if not self.project_url or not self.api_key:
            logger.error("[ERROR] SUPABASE_URL and SUPABASE_API_KEY environment variables required")
            self.connection_failed = True
            return

        # Ensure URL has proper format
        if not self.project_url.startswith("http"):
            self.project_url = f"https://{self.project_url}"

        if not self.project_url.endswith("supabase.co"):
            if not self.project_url.endswith("/"):
                self.project_url += "/"

        self.base_url = f"{self.project_url}/rest/v1"
        self.headers = {
            "apikey": self.api_key,  # Supabase REST API expects 'apikey' header
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        logger.info(f"[*] Supabase REST API configured: {self.project_url}")
        self._test_connection()

    def _make_request(self, method, url, **kwargs):
        """
        Make HTTP request with SSL verification fallback

        If SSL verification fails (common with corporate proxies),
        automatically retry without verification
        """
        try:
            # First attempt with SSL verification enabled
            kwargs['verify'] = self._ssl_verify
            return requests.request(method, url, **kwargs)
        except requests.exceptions.SSLError as ssl_error:
            # If SSL fails and verification is enabled, retry without it
            if self._ssl_verify:
                logger.warning(f"[WARN] SSL verification failed, retrying without verification")
                logger.warning(f"[WARN] This may indicate a corporate proxy or firewall")
                DatabaseManager._ssl_verify = False  # Update class flag
                kwargs['verify'] = False
                return requests.request(method, url, **kwargs)
            else:
                raise

    def _test_connection(self):
        """Test connectivity to Supabase REST API"""
        try:
            logger.info("[*] Testing Supabase REST API connection...")

            response = self._make_request(
                'GET',
                f"{self.base_url}/seen_listings?limit=1",
                headers=self.headers,
                timeout=10
            )

            if response.status_code in [200, 404]:  # 404 is ok if table doesn't exist yet
                logger.info("[OK] Connected to Supabase REST API successfully")
            else:
                logger.error(f"[ERROR] REST API returned status {response.status_code}: {response.text}")
                self.connection_failed = True

        except Exception as e:
            logger.error(f"[ERROR] Failed to connect to Supabase REST API: {e}")
            self.connection_failed = True

    def initialize_schema(self):
        """
        Verify database schema exists
        Note: Tables must be created manually using Supabase SQL Editor
        See setup_database.py for instructions

        Returns:
            True if tables exist, False if missing
        """
        try:
            if self.connection_failed:
                logger.error("[ERROR] Database connection failed - schema initialization skipped")
                return False

            logger.info("[*] Checking database schema...")

            # Check if required tables exist
            required_tables = [
                "seen_listings",
                "vehicle_details",
                "search_configurations",
                "notifications_sent"
            ]

            missing_tables = []

            for table in required_tables:
                try:
                    response = self._make_request(
                        'GET',
                        f"{self.base_url}/{table}?limit=1",
                        headers=self.headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        logger.debug(f"[OK] Table {table} exists")
                    elif response.status_code == 404:
                        logger.error(f"[ERROR] Table {table} does not exist")
                        missing_tables.append(table)
                except Exception as e:
                    logger.error(f"[ERROR] Could not verify table {table}: {e}")
                    missing_tables.append(table)

            if missing_tables:
                logger.error(f"[ERROR] Missing database tables: {', '.join(missing_tables)}")
                logger.error("[ERROR] Please run: python setup_database.py")
                logger.error("[ERROR] Then follow the instructions in setup_database.sql")
                return False

            logger.info("[OK] All required tables exist")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Schema initialization failed: {e}")
            return False

    def has_seen_listing(self, listing_id: str) -> bool:
        """
        Check if listing ID has been seen before

        Args:
            listing_id: The listing ID to check

        Returns:
            True if listing exists, False otherwise
        """
        try:
            if self.connection_failed:
                return False

            response = self._make_request(
                'GET',
                f"{self.base_url}/seen_listings?id=eq.{listing_id}&limit=1",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                results = response.json()
                is_seen = len(results) > 0
                logger.debug(f"[OK] Listing {listing_id} seen: {is_seen}")
                return is_seen
            else:
                logger.warning(f"[WARN] Failed to check listing: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"[WARN] Error checking listing: {e}")
            return False

    def store_listing(self, listing_data: dict) -> bool:
        """
        Store a new listing in database

        Args:
            listing_data: Dictionary containing listing information

        Returns:
            True if successful, False otherwise
        """
        try:
            listing_id = listing_data.get("listing_id")

            if not listing_id:
                logger.error("[ERROR] listing_id is required")
                return False

            if self.connection_failed:
                return False

            logger.debug(f"[*] Storing listing: {listing_id}")

            # Prepare main listing record
            seen_listing = {
                "id": listing_id,
                "created_at": datetime.now().isoformat(),
                "notified": 1
            }

            # Insert into seen_listings
            response = self._make_request(
                'POST',
                f"{self.base_url}/seen_listings",
                headers={**self.headers, "Prefer": "return=minimal"},
                json=seen_listing,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to insert listing: {response.status_code} - {response.text}")
                return False

            # Prepare vehicle details (flatten nested structure for API)
            # New schema uses VARCHAR for all fields - convert values to strings
            vehicle = listing_data.get("vehicle", {})
            engine = listing_data.get("engine", {})
            condition = listing_data.get("condition", {})
            pricing = listing_data.get("pricing", {})
            seller = listing_data.get("seller", {})
            media = listing_data.get("media", {})

            # Helper to convert values to strings for VARCHAR fields
            def to_str(value):
                """Convert any value to string, handling None and booleans"""
                if value is None:
                    return None
                if isinstance(value, bool):
                    return "1" if value else "0"
                return str(value)

            vehicle_details = {
                "listing_id": listing_id,
                # Vehicle identification
                "make": to_str(vehicle.get("make")),
                "model": to_str(vehicle.get("model")),
                "year": to_str(vehicle.get("year")),
                "category": to_str(vehicle.get("category")),
                "vin": to_str(vehicle.get("vin")),
                "modification": to_str(vehicle.get("modification")),

                # Engine/Mechanical
                "fuel_type": to_str(engine.get("fuel_type")),
                "displacement_liters": to_str(engine.get("displacement_liters")),
                "cylinders": to_str(engine.get("cylinders")),
                "transmission": to_str(engine.get("transmission")),
                "power_hp": to_str(engine.get("power_hp")),
                "drive_type": to_str(vehicle.get("drive_type")),

                # Body/Appearance
                "body_type": to_str(vehicle.get("body_type")),
                "color": to_str(vehicle.get("color")),
                "interior_color": to_str(vehicle.get("interior_color")),
                "interior_material": to_str(vehicle.get("interior_material")),
                "wheel_position": to_str(vehicle.get("wheel_position")),
                "doors": to_str(vehicle.get("doors")),
                "seats": to_str(vehicle.get("seats")),

                # Condition
                "status": to_str(condition.get("status")),
                "mileage_km": to_str(condition.get("mileage_km")),
                "mileage_unit": to_str(condition.get("mileage_unit")),
                "customs_cleared": to_str(condition.get("customs_cleared")),
                "technical_inspection_passed": to_str(condition.get("technical_inspection_passed")),
                "condition_description": to_str(condition.get("condition_description")),

                # Pricing
                "price": to_str(pricing.get("price")),
                "currency": to_str(pricing.get("currency")),
                "negotiable": to_str(pricing.get("negotiable")),
                "installment_available": to_str(pricing.get("installment_available")),
                "exchange_possible": to_str(pricing.get("exchange_possible")),

                # Special attributes
                "has_catalytic_converter": to_str(vehicle.get("has_catalytic_converter")),

                # Seller information
                "seller_type": to_str(seller.get("seller_type")),
                "seller_name": to_str(seller.get("seller_name")),
                "seller_phone": to_str(seller.get("seller_phone")),
                "location": to_str(seller.get("location")),
                "is_dealer": to_str(seller.get("is_dealer")),

                # Media
                "primary_image_url": to_str(media.get("primary_image_url")),
                "photo_count": to_str(media.get("photo_count")),
                "video_url": to_str(media.get("video_url")),

                # Metadata
                "posted_date": to_str(listing_data.get("posted_date")),
                "last_updated": to_str(listing_data.get("last_updated")),
                "url": to_str(listing_data.get("url")),
                "view_count": to_str(listing_data.get("view_count")),
                "is_vip": to_str(listing_data.get("is_vip")),
                "is_featured": to_str(listing_data.get("is_featured"))
            }

            # Remove None values to avoid null constraint violations
            vehicle_details = {k: v for k, v in vehicle_details.items() if v is not None}

            # Insert vehicle details
            response = self._make_request(
                'POST',
                f"{self.base_url}/vehicle_details",
                headers={**self.headers, "Prefer": "return=minimal"},
                json=vehicle_details,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to insert vehicle details: {response.status_code} - {response.text}")
                return False

            logger.info(f"[OK] Stored listing: {listing_id}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to store listing: {e}")
            return False

    def record_notification(self, listing_id: str, notification_type: str = "telegram") -> bool:
        """
        Record a sent notification in the database

        Args:
            listing_id: The listing ID that was notified about
            notification_type: Type of notification (telegram, email, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not listing_id:
                logger.error("[ERROR] listing_id is required for notification record")
                return False

            if self.connection_failed:
                return False

            logger.debug(f"[*] Recording notification for listing {listing_id}")

            notification_record = {
                "id": f"{listing_id}-{notification_type}-{datetime.now().isoformat()}",
                "listing_id": listing_id,
                "notification_type": notification_type,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }

            response = self._make_request(
                'POST',
                f"{self.base_url}/notifications_sent",
                headers={**self.headers, "Prefer": "return=minimal"},
                json=notification_record,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.warning(f"[WARN] Failed to record notification: {response.status_code}")
                return False

            logger.debug(f"[OK] Notification recorded for listing {listing_id}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to record notification: {e}")
            return False

    def initialize_search_configurations(self, search_configs: List[Dict]) -> int:
        """
        Initialize search configurations in the database from config file

        Args:
            search_configs: List of search configuration dictionaries from config file

        Returns:
            Number of configurations initialized
        """
        try:
            if not search_configs:
                logger.warning("[WARN] No search configurations to initialize")
                return 0

            if self.connection_failed:
                return 0

            initialized_count = 0

            for config in search_configs:
                try:
                    config_id = config.get("id") or f"search-{datetime.now().isoformat()}"

                    # Check if configuration already exists
                    response = self._make_request(
                        'GET',
                        f"{self.base_url}/search_configurations?id=eq.{config_id}&limit=1",
                        headers=self.headers,
                        timeout=10
                    )

                    if response.status_code == 200 and len(response.json()) > 0:
                        logger.debug(f"[*] Search configuration {config_id} already exists")
                        continue

                    # Insert new configuration
                    search_config_record = {
                        "id": config_id,
                        "name": config.get("name", ""),
                        "base_url": config.get("base_url", ""),
                        "parameters": json.dumps(config.get("parameters", {})),
                        "vehicle_make": config.get("vehicle_make"),
                        "vehicle_model": config.get("vehicle_model"),
                        "year_from": str(config.get("year_from")) if config.get("year_from") else None,
                        "year_to": str(config.get("year_to")) if config.get("year_to") else None,
                        "price_from": str(config.get("price_from")) if config.get("price_from") else None,
                        "price_to": str(config.get("price_to")) if config.get("price_to") else None,
                        "is_active": "1" if config.get("enabled", True) else "0",
                        "created_at": datetime.now().isoformat(),
                        "last_checked_at": None
                    }

                    response = self._make_request(
                        'POST',
                        f"{self.base_url}/search_configurations",
                        headers={**self.headers, "Prefer": "return=minimal"},
                        json=search_config_record,
                        timeout=10
                    )

                    if response.status_code not in [200, 201]:
                        logger.warning(f"[WARN] Failed to initialize search config {config_id}: {response.status_code}")
                        continue

                    logger.info(f"[OK] Initialized search configuration: {config.get('name')}")
                    initialized_count += 1

                except Exception as e:
                    logger.error(f"[ERROR] Failed to initialize search config: {e}")
                    continue

            return initialized_count

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize search configurations: {e}")
            return 0

    def cleanup_old_listings(self, days: int = 365) -> int:
        """
        Delete listings older than specified days

        Args:
            days: Number of days to retain (default: 365)

        Returns:
            Number of listings deleted
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            # First, count how many will be deleted
            response = self._make_request(
                'GET',
                f"{self.base_url}/seen_listings?created_at=lt.{cutoff_date}&select=id",
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                logger.warning(f"[WARN] Could not count old listings: {response.status_code}")
                return 0

            count = len(response.json())

            if count > 0:
                # Delete old listings (cascade should delete vehicle details too)
                response = self._make_request(
                    'DELETE',
                    f"{self.base_url}/seen_listings?created_at=lt.{cutoff_date}",
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code in [200, 204]:
                    logger.info(f"[OK] Cleaned up {count} old listings")
                else:
                    logger.warning(f"[WARN] Cleanup returned status {response.status_code}")

            return count

        except Exception as e:
            logger.warning(f"[WARN] Cleanup failed: {e}")
            return 0

    def get_statistics(self) -> dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        try:
            # Get total count
            response = self._make_request(
                'GET',
                f"{self.base_url}/seen_listings?select=id",
                headers={**self.headers, "Prefer": "count=exact"},
                timeout=10
            )

            total = 0
            if response.status_code == 200:
                if "content-range" in response.headers:
                    # Parse "0-0/1" format
                    range_header = response.headers.get("content-range", "")
                    if "/" in range_header:
                        total = int(range_header.split("/")[1])

            # Get recent count (24h)
            one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
            response = self._make_request(
                'GET',
                f"{self.base_url}/seen_listings?created_at=gt.{one_day_ago}&select=id",
                headers={**self.headers, "Prefer": "count=exact"},
                timeout=10
            )

            recent = 0
            if response.status_code == 200:
                if "content-range" in response.headers:
                    range_header = response.headers.get("content-range", "")
                    if "/" in range_header:
                        recent = int(range_header.split("/")[1])

            return {
                "total_listings": total,
                "recent_listings_24h": recent,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get statistics: {e}")
            return {}

    def close(self):
        """Close database connection (no-op for REST API)"""
        logger.info("[OK] Database connection closed")
