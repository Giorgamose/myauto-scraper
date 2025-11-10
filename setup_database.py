#!/usr/bin/env python3
"""
Database Setup Script - Creates Supabase tables via REST API
Run this once to initialize your Supabase database schema

Usage:
    python setup_database.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.error("[ERROR] requests library not available")
    sys.exit(1)


def get_db_url_and_key():
    """Get Supabase URL and API key from environment"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_API_KEY")

    if not url or not key:
        logger.error("[ERROR] SUPABASE_URL and SUPABASE_API_KEY environment variables required")
        print("\nSet these in .env or .env.local:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_API_KEY=your_api_key_here")
        sys.exit(1)

    return url, key


def execute_sql(url, key, sql):
    """Execute SQL via Supabase RPC"""
    try:
        # Normalize URL
        if not url.startswith("http"):
            url = f"https://{url}"
        if not url.endswith("supabase.co"):
            url = url.rstrip("/")

        # Use the pg_net or pl/pgsql function if available
        # Otherwise, we'll create tables via individual REST API calls
        logger.debug(f"[*] Executing SQL on {url}")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to execute SQL: {e}")
        return False


def create_tables_via_rest(base_url, headers):
    """Create tables by inserting a test record into each table"""
    logger.info("[*] Creating database schema...")

    # Since REST API doesn't allow arbitrary SQL, we'll document what needs to be created
    # and provide the SQL for the user to run manually in Supabase console

    sql_statements = """
    -- Supabase Database Schema for MyAuto Car Listing Monitor
    -- Run these commands in your Supabase SQL Editor

    -- Table 1: seen_listings (main listing tracking)
    CREATE TABLE IF NOT EXISTS seen_listings (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        last_notified_at TEXT,
        notified INTEGER DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_listings_created_at ON seen_listings(created_at);

    -- Table 2: vehicle_details (full vehicle information)
    CREATE TABLE IF NOT EXISTS vehicle_details (
        listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,
        make TEXT, make_id INTEGER, model TEXT, model_id INTEGER, modification TEXT,
        year INTEGER, vin TEXT, body_type TEXT, color TEXT, interior_color TEXT,
        doors INTEGER, seats INTEGER, wheel_position TEXT, drive_type TEXT,
        fuel_type TEXT, fuel_type_id INTEGER, displacement_liters REAL,
        transmission TEXT, power_hp INTEGER, cylinders INTEGER,
        status TEXT, mileage_km INTEGER, mileage_unit TEXT,
        customs_cleared INTEGER, technical_inspection_passed INTEGER,
        condition_description TEXT, price REAL, currency TEXT, currency_id INTEGER,
        negotiable INTEGER, installment_available INTEGER, exchange_possible INTEGER,
        seller_type TEXT, seller_name TEXT, seller_phone TEXT,
        location TEXT, location_id INTEGER, is_dealer INTEGER, dealer_id INTEGER,
        primary_image_url TEXT, photo_count INTEGER, video_url TEXT,
        posted_date TEXT, last_updated TEXT, url TEXT,
        view_count INTEGER, is_vip INTEGER, is_featured INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_vehicle_make ON vehicle_details(make);

    -- Table 3: search_configurations (search settings)
    CREATE TABLE IF NOT EXISTS search_configurations (
        id SERIAL PRIMARY KEY,
        name TEXT,
        search_url TEXT,
        vehicle_make TEXT,
        vehicle_model TEXT,
        year_from INTEGER,
        year_to INTEGER,
        price_from REAL,
        price_to REAL,
        currency_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT NOW(),
        last_checked_at TIMESTAMP
    );

    -- Table 4: notifications_sent (notification tracking)
    CREATE TABLE IF NOT EXISTS notifications_sent (
        id SERIAL PRIMARY KEY,
        listing_id TEXT REFERENCES seen_listings(id) ON DELETE CASCADE,
        notification_type TEXT,
        sent_at TIMESTAMP DEFAULT NOW(),
        telegram_message_id TEXT,
        success INTEGER DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_sent(sent_at);
    """

    return sql_statements


def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("  Supabase Database Setup - MyAuto Car Listing Monitor")
    print("="*70 + "\n")

    url, key = get_db_url_and_key()

    logger.info(f"[*] Supabase Project URL: {url}")
    logger.info(f"[*] API Key: {key[:20]}...")

    print("\n" + "="*70)
    print("  SETUP INSTRUCTIONS")
    print("="*70 + "\n")

    print("""
The REST API cannot directly execute CREATE TABLE statements.
You must create the database schema manually:

OPTION 1: Using Supabase Dashboard (Easiest)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://app.supabase.com
2. Select your project: efohkibukutjvrrhhxdn
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Copy and paste the SQL below
6. Click "Run"

OPTION 2: Using psql Command Line
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Get your database password from Supabase Dashboard
2. Run:

    psql -h db.efohkibukutjvrrhhxdn.supabase.co \\
         -U postgres \\
         -d postgres \\
         -c "$(cat <<'SQL'
    <paste SQL below>
    SQL
    )"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""")

    # Get and print SQL statements
    sql = create_tables_via_rest(url + "/rest/v1", {})

    print("SQL SCRIPT TO CREATE TABLES:")
    print("="*70)
    print(sql)
    print("="*70)

    # Save to file
    sql_file = "setup_database.sql"
    with open(sql_file, "w") as f:
        f.write(sql)

    logger.info(f"\n[OK] SQL script saved to: {sql_file}")
    logger.info("[OK] Copy this SQL to your Supabase SQL Editor and run it")

    print("\n" + "="*70)
    print("  VERIFICATION")
    print("="*70 + "\n")

    print("""
After creating the tables, verify they exist by running:

    python query_db.py stats

Or run the monitoring cycle:

    python main.py

""")


if __name__ == "__main__":
    main()
