#!/usr/bin/env python3
"""
Database Manager - Supabase PostgreSQL Operations
Handles all database interactions for listing storage and retrieval
"""

import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except Exception as e:
    logger.warning(f"[WARN] Could not import psycopg2: {e}")
    PSYCOPG2_AVAILABLE = False


class DatabaseManager:
    """Manage Supabase PostgreSQL database operations for car listings"""

    def __init__(self, db_url: str):
        """Initialize database connection - Args: db_url: PostgreSQL connection string from Supabase"""
        self.db_url = db_url
        self.conn = None
        self.connection_failed = False

        if not PSYCOPG2_AVAILABLE:
            logger.warning("[WARN] psycopg2 not available - install: pip install psycopg2-binary")
            self.connection_failed = True
            return

        try:
            logger.info("[*] Connecting to Supabase PostgreSQL database...")
            self.conn = psycopg2.connect(db_url)
            logger.info("[OK] Connected to Supabase database successfully")
        except Exception as e:
            import traceback
            logger.error(f"[ERROR] Failed to connect: {e}")
            logger.debug(f"[DEBUG] {traceback.format_exc()}")
            self.conn = None
            self.connection_failed = True

    def _execute(self, query: str, params=None):
        """Execute SQL query safely"""
        if self.connection_failed or not self.conn:
            return None

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or [])

            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self.conn.commit()
                cursor.close()
                return True

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"[ERROR] Query failed: {e}")
            return None

    def initialize_schema(self):
        """Create database schema if not exists"""
        try:
            if self.connection_failed:
                logger.debug("[*] Database unavailable")
                return True

            logger.info("[*] Initializing database schema...")

            self._execute("CREATE TABLE IF NOT EXISTS seen_listings (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, last_notified_at TEXT, notified INTEGER DEFAULT 0)")
            logger.debug("[OK] seen_listings table created")

            self._execute("""CREATE TABLE IF NOT EXISTS vehicle_details (
                listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,
                make TEXT, make_id INTEGER, model TEXT, model_id INTEGER, modification TEXT, year INTEGER, vin TEXT,
                body_type TEXT, color TEXT, interior_color TEXT, doors INTEGER, seats INTEGER, wheel_position TEXT, drive_type TEXT,
                fuel_type TEXT, fuel_type_id INTEGER, displacement_liters REAL, transmission TEXT, power_hp INTEGER, cylinders INTEGER,
                status TEXT, mileage_km INTEGER, mileage_unit TEXT, customs_cleared INTEGER, technical_inspection_passed INTEGER,
                condition_description TEXT, price REAL, currency TEXT, currency_id INTEGER, negotiable INTEGER,
                installment_available INTEGER, exchange_possible INTEGER, seller_type TEXT, seller_name TEXT, seller_phone TEXT,
                location TEXT, location_id INTEGER, is_dealer INTEGER, dealer_id INTEGER, primary_image_url TEXT, photo_count INTEGER,
                video_url TEXT, posted_date TEXT, last_updated TEXT, url TEXT, view_count INTEGER, is_vip INTEGER, is_featured INTEGER
            )""")
            logger.debug("[OK] vehicle_details table created")

            self._execute("CREATE TABLE IF NOT EXISTS search_configurations (id SERIAL PRIMARY KEY, name TEXT, search_url TEXT, vehicle_make TEXT, vehicle_model TEXT, year_from INTEGER, year_to INTEGER, price_from REAL, price_to REAL, currency_id INTEGER, is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT NOW(), last_checked_at TIMESTAMP)")

            self._execute("CREATE TABLE IF NOT EXISTS notifications_sent (id SERIAL PRIMARY KEY, listing_id TEXT REFERENCES seen_listings(id) ON DELETE CASCADE, notification_type TEXT, sent_at TIMESTAMP DEFAULT NOW(), telegram_message_id TEXT, success INTEGER DEFAULT 0)")

            self._execute("CREATE INDEX IF NOT EXISTS idx_listings_created_at ON seen_listings(created_at)")
            self._execute("CREATE INDEX IF NOT EXISTS idx_vehicle_make ON vehicle_details(make)")
            self._execute("CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_sent(sent_at)")

            logger.info("[OK] Database schema initialized successfully")
            return True

        except Exception as e:
            logger.debug(f"[*] Schema init error: {e}")
            self.connection_failed = True
            return True

    def has_seen_listing(self, listing_id: str) -> bool:
        """Check if listing ID has been seen before"""
        try:
            if self.connection_failed:
                return False

            result = self._execute("SELECT 1 FROM seen_listings WHERE id = %s", [listing_id])
            is_seen = len(result) > 0 if result else False
            logger.debug(f"[OK] Listing {listing_id} seen: {is_seen}")
            return is_seen

        except Exception as e:
            logger.warning(f"[WARN] Error checking listing: {e}")
            return False

    def store_listing(self, listing_data: dict) -> bool:
        """Store a new listing in database"""
        try:
            listing_id = listing_data.get("listing_id")

            if not listing_id:
                logger.error("[ERROR] listing_id is required")
                return False

            if self.connection_failed:
                return False

            logger.debug(f"[*] Storing listing: {listing_id}")

            self._execute("INSERT INTO seen_listings (id, created_at, notified) VALUES (%s, %s, %s)", [listing_id, datetime.now().isoformat(), 1])

            vehicle = listing_data.get("vehicle", {})
            engine = listing_data.get("engine", {})
            condition = listing_data.get("condition", {})
            pricing = listing_data.get("pricing", {})
            seller = listing_data.get("seller", {})
            media = listing_data.get("media", {})

            self._execute("""INSERT INTO vehicle_details (
                listing_id, make, make_id, model, model_id, modification, year, vin,
                body_type, color, interior_color, doors, seats, wheel_position, drive_type,
                fuel_type, fuel_type_id, displacement_liters, transmission, power_hp, cylinders,
                status, mileage_km, mileage_unit, customs_cleared, technical_inspection_passed,
                condition_description, price, currency, currency_id, negotiable,
                installment_available, exchange_possible, seller_type, seller_name, seller_phone,
                location, location_id, is_dealer, dealer_id, primary_image_url, photo_count,
                video_url, posted_date, last_updated, url, view_count, is_vip, is_featured
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", [
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

    def cleanup_old_listings(self, days: int = 365) -> int:
        """Delete listings older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            count_result = self._execute("SELECT COUNT(*) as count FROM seen_listings WHERE created_at < %s", [cutoff_date])
            count = count_result[0]['count'] if count_result else 0

            if count > 0:
                self._execute("DELETE FROM seen_listings WHERE created_at < %s", [cutoff_date])
                logger.info(f"[OK] Cleaned up {count} old listings")

            return count

        except Exception as e:
            logger.warning(f"[WARN] Cleanup failed: {e}")
            return 0

    def get_statistics(self) -> dict:
        """Get database statistics"""
        try:
            total_result = self._execute("SELECT COUNT(*) as count FROM seen_listings")
            total = total_result[0]['count'] if total_result else 0

            one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()

            recent_result = self._execute("SELECT COUNT(*) as count FROM seen_listings WHERE created_at > %s", [one_day_ago])
            recent = recent_result[0]['count'] if recent_result else 0

            return {
                "total_listings": total,
                "recent_listings_24h": recent,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get statistics: {e}")
            return {}

    def close(self):
        """Close database connection"""
        try:
            if self.conn:
                self.conn.close()
                logger.info("[OK] Database connection closed")
        except Exception as e:
            logger.error(f"[ERROR] Failed to close connection: {e}")
