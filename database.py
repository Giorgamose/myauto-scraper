#!/usr/bin/env python3
"""
Database Manager - Turso SQLite Database Operations
Handles all database interactions for listing storage and retrieval
"""

import logging
from datetime import datetime, timedelta
from libsql_client import create_client_sync
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage Turso database operations for car listings"""

    def __init__(self, db_url: str, auth_token: str):
        """
        Initialize database connection

        Args:
            db_url: Turso database URL (libsql://...)
            auth_token: Turso authentication token
        """

        self.db_url = db_url
        self.auth_token = auth_token
        self.client = None

        try:
            self.client = create_client_sync(url=db_url, auth_token=auth_token)
            logger.info("[OK] Connected to Turso database")
        except Exception as e:
            logger.error(f"[ERROR] Failed to connect to database: {e}")
            raise

    def initialize_schema(self):
        """Create database schema if not exists"""

        try:
            logger.info("[*] Initializing database schema...")

            # Create tables
            self.client.execute("""
                CREATE TABLE IF NOT EXISTS seen_listings (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_notified_at TIMESTAMP,
                    notified BOOLEAN DEFAULT 1
                )
            """)

            self.client.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_details (
                    listing_id TEXT PRIMARY KEY,
                    make TEXT,
                    make_id INTEGER,
                    model TEXT,
                    model_id INTEGER,
                    modification TEXT,
                    year INTEGER,
                    vin TEXT UNIQUE,
                    body_type TEXT,
                    color TEXT,
                    interior_color TEXT,
                    doors INTEGER,
                    seats INTEGER,
                    wheel_position TEXT,
                    drive_type TEXT,
                    fuel_type TEXT,
                    fuel_type_id INTEGER,
                    displacement_liters REAL,
                    transmission TEXT,
                    power_hp INTEGER,
                    cylinders INTEGER,
                    status TEXT,
                    mileage_km INTEGER,
                    mileage_unit TEXT,
                    customs_cleared BOOLEAN,
                    technical_inspection_passed BOOLEAN,
                    condition_description TEXT,
                    price REAL,
                    currency TEXT,
                    currency_id INTEGER,
                    negotiable BOOLEAN,
                    installment_available BOOLEAN,
                    exchange_possible BOOLEAN,
                    seller_type TEXT,
                    seller_name TEXT,
                    seller_phone TEXT,
                    location TEXT,
                    location_id INTEGER,
                    is_dealer BOOLEAN,
                    dealer_id INTEGER,
                    primary_image_url TEXT,
                    photo_count INTEGER,
                    video_url TEXT,
                    posted_date TIMESTAMP,
                    last_updated TIMESTAMP,
                    url TEXT,
                    view_count INTEGER,
                    is_vip BOOLEAN,
                    is_featured BOOLEAN
                )
            """)

            self.client.execute("""
                CREATE TABLE IF NOT EXISTS search_configurations (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    search_url TEXT,
                    vehicle_make TEXT,
                    vehicle_model TEXT,
                    year_from INTEGER,
                    year_to INTEGER,
                    price_from REAL,
                    price_to REAL,
                    currency_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checked_at TIMESTAMP
                )
            """)

            self.client.execute("""
                CREATE TABLE IF NOT EXISTS notifications_sent (
                    id INTEGER PRIMARY KEY,
                    listing_id TEXT,
                    notification_type TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    telegram_message_id TEXT,
                    success BOOLEAN
                )
            """)

            # Create indexes
            self.client.execute("""
                CREATE INDEX IF NOT EXISTS idx_seen_listings_created_at
                ON seen_listings(created_at)
            """)

            self.client.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicle_details_year
                ON vehicle_details(year)
            """)

            self.client.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicle_details_price
                ON vehicle_details(price)
            """)

            self.client.execute("""
                CREATE INDEX IF NOT EXISTS idx_vehicle_details_posted_date
                ON vehicle_details(posted_date)
            """)

            logger.info("[OK] Database schema initialized successfully")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize schema: {e}")
            return False

    def has_seen_listing(self, listing_id: str) -> bool:
        """
        Check if listing ID has been seen before

        Args:
            listing_id: MyAuto.ge listing ID

        Returns:
            True if seen, False otherwise
        """

        try:
            result = self.client.execute(
                "SELECT 1 FROM seen_listings WHERE id = ?",
                [listing_id]
            )

            return len(result) > 0

        except Exception as e:
            logger.error(f"[ERROR] Error checking listing: {e}")
            return False

    def store_listing(self, listing_data: dict) -> bool:
        """
        Store a new listing in database

        Args:
            listing_data: Dictionary with listing details

        Returns:
            True if successful, False otherwise
        """

        try:
            listing_id = listing_data.get("listing_id")

            if not listing_id:
                logger.error("[ERROR] listing_id is required")
                return False

            now = datetime.now().isoformat()

            # Insert into seen_listings
            self.client.execute(
                "INSERT INTO seen_listings (id, created_at, notified) VALUES (?, ?, ?)",
                [listing_id, now, 1]
            )

            # Insert into vehicle_details
            vehicle = listing_data.get("vehicle", {})
            engine = listing_data.get("engine", {})
            condition = listing_data.get("condition", {})
            pricing = listing_data.get("pricing", {})
            seller = listing_data.get("seller", {})
            media = listing_data.get("media", {})

            self.client.execute("""
                INSERT INTO vehicle_details (
                    listing_id, make, make_id, model, model_id, modification, year, vin,
                    body_type, color, interior_color, doors, seats, wheel_position, drive_type,
                    fuel_type, fuel_type_id, displacement_liters, transmission, power_hp, cylinders,
                    status, mileage_km, mileage_unit, customs_cleared, technical_inspection_passed,
                    condition_description, price, currency, currency_id, negotiable,
                    installment_available, exchange_possible, seller_type, seller_name, seller_phone,
                    location, location_id, is_dealer, dealer_id, primary_image_url, photo_count,
                    video_url, posted_date, last_updated, url, view_count, is_vip, is_featured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                listing_id,
                vehicle.get("make"), vehicle.get("make_id"),
                vehicle.get("model"), vehicle.get("model_id"),
                vehicle.get("modification"), vehicle.get("year"), vehicle.get("vin"),
                vehicle.get("body_type"), vehicle.get("color"), vehicle.get("interior_color"),
                vehicle.get("doors"), vehicle.get("seats"), vehicle.get("wheel_position"),
                vehicle.get("drive_type"),
                engine.get("fuel_type"), engine.get("fuel_type_id"),
                engine.get("displacement_liters"), engine.get("transmission"),
                engine.get("power_hp"), engine.get("cylinders"),
                condition.get("status"), condition.get("mileage_km"),
                condition.get("mileage_unit"), condition.get("customs_cleared"),
                condition.get("technical_inspection_passed"), condition.get("condition_description"),
                pricing.get("price"), pricing.get("currency"), pricing.get("currency_id"),
                pricing.get("negotiable"), pricing.get("installment_available"),
                pricing.get("exchange_possible"),
                seller.get("seller_type"), seller.get("seller_name"), seller.get("seller_phone"),
                seller.get("location"), seller.get("location_id"),
                seller.get("is_dealer"), seller.get("dealer_id"),
                media.get("primary_image_url"), media.get("photo_count"),
                media.get("video_url"),
                listing_data.get("posted_date"), listing_data.get("last_updated"),
                listing_data.get("url"), listing_data.get("view_count"),
                listing_data.get("is_vip"), listing_data.get("is_featured")
            ])

            logger.info(f"[OK] Stored listing: {listing_id}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to store listing: {e}")
            return False

    def get_recent_listings(self, days: int = 7, limit: int = 100) -> list:
        """
        Get recently added listings

        Args:
            days: Get listings from last N days
            limit: Maximum number to return

        Returns:
            List of listing dictionaries
        """

        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            result = self.client.execute(
                f"""
                SELECT sl.id, vd.*
                FROM seen_listings sl
                LEFT JOIN vehicle_details vd ON sl.id = vd.listing_id
                WHERE sl.created_at > ?
                ORDER BY sl.created_at DESC
                LIMIT ?
                """,
                [cutoff_date, limit]
            )

            return result

        except Exception as e:
            logger.error(f"[ERROR] Failed to get recent listings: {e}")
            return []

    def log_notification(self, listing_id: str, notification_type: str,
                        success: bool, message_id: str = None) -> bool:
        """
        Log a sent notification

        Args:
            listing_id: Listing ID
            notification_type: Type (new_listing, no_listings, error)
            success: Whether notification was successful
            message_id: Telegram message ID if successful

        Returns:
            True if logged successfully
        """

        try:
            self.client.execute(
                """INSERT INTO notifications_sent
                   (listing_id, notification_type, success, telegram_message_id)
                   VALUES (?, ?, ?, ?)""",
                [listing_id, notification_type, 1 if success else 0, message_id]
            )

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to log notification: {e}")
            return False

    def cleanup_old_listings(self, days: int = 365) -> int:
        """
        Delete listings older than specified days

        Args:
            days: Delete listings older than N days

        Returns:
            Number of listings deleted
        """

        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Get count before deletion
            count_result = self.client.execute(
                "SELECT COUNT(*) as count FROM seen_listings WHERE created_at < ?",
                [cutoff_date]
            )

            count = count_result[0][0] if count_result else 0

            if count > 0:
                self.client.execute(
                    "DELETE FROM seen_listings WHERE created_at < ?",
                    [cutoff_date]
                )

                logger.info(f"[OK] Cleaned up {count} old listings")

            return count

        except Exception as e:
            logger.error(f"[ERROR] Failed to cleanup listings: {e}")
            return 0

    def update_last_checked(self, search_id: int) -> bool:
        """
        Update last checked timestamp for a search

        Args:
            search_id: Search configuration ID

        Returns:
            True if successful
        """

        try:
            self.client.execute(
                "UPDATE search_configurations SET last_checked_at = ? WHERE id = ?",
                [datetime.now().isoformat(), search_id]
            )

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to update last checked: {e}")
            return False

    def get_statistics(self) -> dict:
        """
        Get database statistics

        Returns:
            Dictionary with stats
        """

        try:
            total_result = self.client.execute(
                "SELECT COUNT(*) as count FROM seen_listings"
            )
            total = total_result[0][0] if total_result else 0

            recent_result = self.client.execute(
                "SELECT COUNT(*) as count FROM seen_listings WHERE created_at > datetime('now', '-1 day')"
            )
            recent = recent_result[0][0] if recent_result else 0

            notified_result = self.client.execute(
                "SELECT COUNT(*) as count FROM notifications_sent WHERE sent_at > datetime('now', '-1 day') AND success = 1"
            )
            notified = notified_result[0][0] if notified_result else 0

            return {
                "total_listings": total,
                "recent_listings_24h": recent,
                "notifications_sent_24h": notified,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get statistics: {e}")
            return {}

    def close(self):
        """Close database connection"""

        try:
            if self.client:
                # Turso client doesn't have explicit close, but we can log
                logger.info("[OK] Database connection closed")
        except Exception as e:
            logger.error(f"[ERROR] Failed to close connection: {e}")


def test_database():
    """Test database connection and operations"""

    db_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not db_url or not auth_token:
        logger.error("[ERROR] Missing database credentials")
        return False

    try:
        db = DatabaseManager(db_url, auth_token)
        logger.info("[OK] Database connected")

        # Initialize schema
        if db.initialize_schema():
            logger.info("[OK] Schema initialized")

            # Get stats
            stats = db.get_statistics()
            logger.info(f"[OK] Stats: {stats}")

            db.close()
            return True

        return False

    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(0 if test_database() else 1)
