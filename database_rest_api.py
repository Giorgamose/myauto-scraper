#!/usr/bin/env python3
"""
Database Manager - Supabase REST API Operations
Handles all database interactions using Supabase REST API (no direct PostgreSQL)
This avoids IPv6 connectivity issues that occur with direct connections in GitHub Actions
"""

import logging
from datetime import datetime, timedelta
import os
import json

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception as e:
    logger.warning(f"[WARN] Could not import requests: {e}")
    REQUESTS_AVAILABLE = False


class DatabaseManager:
    """Manage Supabase database operations using REST API instead of direct PostgreSQL"""

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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        logger.info(f"[*] Supabase REST API configured: {self.project_url}")
        self._test_connection()

    def _test_connection(self):
        """Test connectivity to Supabase REST API"""
        try:
            logger.info("[*] Testing Supabase REST API connection...")
            response = requests.get(
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
        Create database tables if they don't exist
        Uses raw SQL execution via Supabase RPC or direct table creation via REST API

        Returns:
            True if successful, False if failed
        """
        try:
            if self.connection_failed:
                logger.error("[ERROR] Database connection failed - schema initialization skipped")
                return False

            logger.info("[*] Initializing database schema...")

            # Check if tables exist by trying to query them
            tables_to_create = [
                "seen_listings",
                "vehicle_details",
                "search_configurations",
                "notifications_sent"
            ]

            for table in tables_to_create:
                try:
                    response = requests.get(
                        f"{self.base_url}/{table}?limit=1",
                        headers=self.headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        logger.debug(f"[OK] Table {table} exists")
                    elif response.status_code == 404:
                        logger.warning(f"[WARN] Table {table} does not exist. Manual creation required.")
                except Exception as e:
                    logger.warning(f"[WARN] Could not verify table {table}: {e}")

            logger.info("[OK] Database schema check completed")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Schema initialization failed: {e}")
            self.connection_failed = True
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

            response = requests.get(
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
            response = requests.post(
                f"{self.base_url}/seen_listings",
                headers={**self.headers, "Prefer": "return=minimal"},
                json=seen_listing,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to insert listing: {response.status_code} - {response.text}")
                return False

            # Prepare vehicle details (flatten nested structure for API)
            vehicle = listing_data.get("vehicle", {})
            engine = listing_data.get("engine", {})
            condition = listing_data.get("condition", {})
            pricing = listing_data.get("pricing", {})
            seller = listing_data.get("seller", {})
            media = listing_data.get("media", {})

            vehicle_details = {
                "listing_id": listing_id,
                "make": vehicle.get("make"),
                "make_id": vehicle.get("make_id"),
                "model": vehicle.get("model"),
                "model_id": vehicle.get("model_id"),
                "modification": vehicle.get("modification"),
                "year": vehicle.get("year"),
                "vin": vehicle.get("vin"),
                "body_type": vehicle.get("body_type"),
                "color": vehicle.get("color"),
                "interior_color": vehicle.get("interior_color"),
                "doors": vehicle.get("doors"),
                "seats": vehicle.get("seats"),
                "wheel_position": vehicle.get("wheel_position"),
                "drive_type": vehicle.get("drive_type"),
                "fuel_type": engine.get("fuel_type"),
                "fuel_type_id": engine.get("fuel_type_id"),
                "displacement_liters": engine.get("displacement_liters"),
                "transmission": engine.get("transmission"),
                "power_hp": engine.get("power_hp"),
                "cylinders": engine.get("cylinders"),
                "status": condition.get("status"),
                "mileage_km": condition.get("mileage_km"),
                "mileage_unit": condition.get("mileage_unit"),
                "customs_cleared": condition.get("customs_cleared"),
                "technical_inspection_passed": condition.get("technical_inspection_passed"),
                "condition_description": condition.get("condition_description"),
                "price": pricing.get("price"),
                "currency": pricing.get("currency"),
                "currency_id": pricing.get("currency_id"),
                "negotiable": pricing.get("negotiable"),
                "installment_available": pricing.get("installment_available"),
                "exchange_possible": pricing.get("exchange_possible"),
                "seller_type": seller.get("seller_type"),
                "seller_name": seller.get("seller_name"),
                "seller_phone": seller.get("seller_phone"),
                "location": seller.get("location"),
                "location_id": seller.get("location_id"),
                "is_dealer": seller.get("is_dealer"),
                "dealer_id": seller.get("dealer_id"),
                "primary_image_url": media.get("primary_image_url"),
                "photo_count": media.get("photo_count"),
                "video_url": media.get("video_url"),
                "posted_date": listing_data.get("posted_date"),
                "last_updated": listing_data.get("last_updated"),
                "url": listing_data.get("url"),
                "view_count": listing_data.get("view_count"),
                "is_vip": listing_data.get("is_vip"),
                "is_featured": listing_data.get("is_featured")
            }

            # Remove None values to avoid null constraint violations
            vehicle_details = {k: v for k, v in vehicle_details.items() if v is not None}

            # Insert vehicle details
            response = requests.post(
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
            response = requests.get(
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
                response = requests.delete(
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
            response = requests.get(
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
            response = requests.get(
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
