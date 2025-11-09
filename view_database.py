#!/usr/bin/env python3
"""
Database Viewer - Display scraped records from Turso SQLite
View all Toyota Prado listings and other vehicles in your database
"""

import os
import sys
from datetime import datetime
from libsql_client import create_client_sync

print("\n" + "="*80)
print("MYAUTO SCRAPER - DATABASE VIEWER")
print("="*80)

# Get database credentials from environment
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
    print("\n[ERROR] Missing environment variables!")
    print("\nSet these environment variables:")
    print("  TURSO_DATABASE_URL  - Your Turso database URL")
    print("  TURSO_AUTH_TOKEN    - Your Turso authentication token")
    print("\nExample:")
    print("  set TURSO_DATABASE_URL=libsql://your-db.turso.io")
    print("  set TURSO_AUTH_TOKEN=your-token-here")
    sys.exit(1)

print("\n[*] Connecting to Turso database...")

try:
    # Create database connection
    client = create_client_sync(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )
    print("[OK] Connected to database")

except Exception as e:
    print(f"[ERROR] Failed to connect to database: {e}")
    print("\nTroubleshooting:")
    print("  1. Verify TURSO_DATABASE_URL is correct")
    print("  2. Verify TURSO_AUTH_TOKEN is correct")
    print("  3. Check internet connection")
    print("  4. Verify database exists in turso.tech dashboard")
    sys.exit(1)

# ============================================================================
# PART 1: VIEW ALL RECORDS
# ============================================================================
print("\n[PART 1] ALL SCRAPED RECORDS")
print("-" * 80)

try:
    result = client.execute("SELECT COUNT(*) as count FROM vehicle_details")
    total_records = result.rows[0][0] if result.rows else 0
    print(f"\nTotal records in database: {total_records}")

    if total_records == 0:
        print("\n[INFO] No records yet. The database will be populated as the scraper runs.")
        print("\nExpected workflow:")
        print("  1. Scraper runs every 10 minutes")
        print("  2. Finds matching Toyota Prado listings")
        print("  3. Stores 31 data fields per listing")
        print("  4. Records appear here")

    else:
        print(f"\n[OK] Found {total_records} scraped records")

        # Show column names
        print("\nColumns available in vehicle_details table:")
        print("-" * 80)
        columns = [
            "listing_id", "title", "description", "price", "currency",
            "make", "model", "year", "mileage", "transmission",
            "body_type", "color", "engine_volume", "fuel_type",
            "condition", "owners_count", "accident_history", "customs_cleared",
            "registration_location", "seller_name", "seller_phone",
            "seller_email", "posted_date", "view_count", "favorite_count",
            "url", "created_at"
        ]
        for i, col in enumerate(columns, 1):
            print(f"  {i:2}. {col}")

except Exception as e:
    print(f"[ERROR] Failed to query database: {e}")
    sys.exit(1)

# ============================================================================
# PART 2: SAMPLE RECORDS
# ============================================================================
print("\n[PART 2] SAMPLE RECORDS (Latest 5)")
print("-" * 80)

try:
    result = client.execute("""
        SELECT listing_id, title, make, model, year, price, currency,
               fuel_type, transmission, mileage, seller_phone, created_at
        FROM vehicle_details
        ORDER BY created_at DESC
        LIMIT 5
    """)

    if result.rows:
        print("\nLatest 5 records:\n")
        for row in result.rows:
            print(f"Listing ID:     {row[0]}")
            print(f"Title:          {row[1]}")
            print(f"Make:           {row[2]}")
            print(f"Model:          {row[3]}")
            print(f"Year:           {row[4]}")
            print(f"Price:          {row[5]} {row[6]}")
            print(f"Fuel Type:      {row[7]}")
            print(f"Transmission:   {row[8]}")
            print(f"Mileage:        {row[9]} km")
            print(f"Seller Phone:   {row[10]}")
            print(f"Scraped At:     {row[11]}")
            print("-" * 80)
    else:
        print("\n[INFO] No records found in database yet")

except Exception as e:
    print(f"[ERROR] Failed to fetch sample records: {e}")

# ============================================================================
# PART 3: TOYOTA PRADO RECORDS (Your Search)
# ============================================================================
print("\n[PART 3] TOYOTA PRADO RECORDS (Your Search)")
print("-" * 80)

try:
    result = client.execute("""
        SELECT COUNT(*) as count FROM vehicle_details
        WHERE make = 'Toyota' AND model = 'Land Cruiser Prado'
    """)

    prado_count = result.rows[0][0] if result.rows else 0
    print(f"\nToyota Prado records: {prado_count}")

    if prado_count > 0:
        result = client.execute("""
            SELECT listing_id, title, year, price, currency, mileage,
                   fuel_type, transmission, seller_name, seller_phone, created_at
            FROM vehicle_details
            WHERE make = 'Toyota' AND model = 'Land Cruiser Prado'
            ORDER BY created_at DESC
            LIMIT 10
        """)

        print("\nToyota Prado listings found:\n")
        for i, row in enumerate(result.rows, 1):
            print(f"[{i}] {row[1]} (ID: {row[0]})")
            print(f"    Year: {row[2]}, Price: {row[3]} {row[4]}, Mileage: {row[5]} km")
            print(f"    Fuel: {row[6]}, Transmission: {row[7]}")
            print(f"    Seller: {row[8]} - {row[9]}")
            print(f"    Found: {row[10]}")
            print()
    else:
        print("\n[INFO] No Toyota Prado records yet")
        print("\nYour search criteria:")
        print("  Make: Toyota")
        print("  Model: Land Cruiser Prado")
        print("  Year: 1995-2008")
        print("  Price: 11,000 - 18,000 GEL")
        print("  Fuel: Diesel")
        print("  Customs: Cleared")
        print("\nRecords will appear here as the scraper finds matches.")

except Exception as e:
    print(f"[ERROR] Failed to query Toyota Prado records: {e}")

# ============================================================================
# PART 4: STATISTICS
# ============================================================================
print("\n[PART 4] STATISTICS")
print("-" * 80)

try:
    # Price statistics
    result = client.execute("""
        SELECT MIN(price), MAX(price), AVG(price), COUNT(*)
        FROM vehicle_details
        WHERE price > 0
    """)

    if result.rows and result.rows[0][3] > 0:
        min_price, max_price, avg_price, count = result.rows[0]
        print(f"\nPrice Statistics ({count} records with price):")
        print(f"  Minimum:  {min_price} GEL")
        print(f"  Maximum:  {max_price} GEL")
        print(f"  Average:  {avg_price:.0f} GEL")

    # Year statistics
    result = client.execute("""
        SELECT MIN(year), MAX(year), COUNT(*)
        FROM vehicle_details
        WHERE year > 1900
    """)

    if result.rows and result.rows[0][2] > 0:
        min_year, max_year, count = result.rows[0]
        print(f"\nYear Statistics ({count} records with year):")
        print(f"  Oldest:   {min_year}")
        print(f"  Newest:   {max_year}")

    # Fuel type breakdown
    result = client.execute("""
        SELECT fuel_type, COUNT(*) as count
        FROM vehicle_details
        WHERE fuel_type IS NOT NULL
        GROUP BY fuel_type
        ORDER BY count DESC
    """)

    if result.rows:
        print(f"\nFuel Type Breakdown:")
        for row in result.rows:
            print(f"  {row[0]:.<20} {row[1]:>3} records")

    # Make/Model breakdown
    result = client.execute("""
        SELECT make, model, COUNT(*) as count
        FROM vehicle_details
        WHERE make IS NOT NULL AND model IS NOT NULL
        GROUP BY make, model
        ORDER BY count DESC
        LIMIT 10
    """)

    if result.rows:
        print(f"\nTop Makes/Models:")
        for row in result.rows:
            print(f"  {row[0]} {row[1]:.<30} {row[2]:>3} records")

except Exception as e:
    print(f"[ERROR] Failed to fetch statistics: {e}")

# ============================================================================
# PART 5: SEEN LISTINGS (Deduplication Check)
# ============================================================================
print("\n[PART 5] DEDUPLICATION STATUS")
print("-" * 80)

try:
    result = client.execute("SELECT COUNT(*) as count FROM seen_listings")
    seen_count = result.rows[0][0] if result.rows else 0
    print(f"\nTotal unique listings tracked: {seen_count}")
    print("\nThese listing IDs are checked to prevent duplicate notifications")
    print("When a listing is found again, it's skipped (no notification sent)")

except Exception as e:
    print(f"[ERROR] Failed to query deduplication status: {e}")

# ============================================================================
# PART 6: DATABASE INFO
# ============================================================================
print("\n[PART 6] DATABASE INFORMATION")
print("-" * 80)

print(f"\nDatabase URL:       {TURSO_DATABASE_URL}")
print(f"Connection Status:  Connected")
print(f"Query Time:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\nDatabase Tables:")
print("  1. vehicle_details - All scraped car listings (31 fields per record)")
print("  2. seen_listings   - Tracking unique listing IDs (deduplication)")

print("\nData Retention:")
print("  Records kept for:  1 year (365 days)")
print("  Auto-cleanup:      Every 10th run")
print("  Retention policy:  Delete records older than 365 days")

# ============================================================================
# DONE
# ============================================================================
print("\n" + "="*80)
print("DATABASE VIEWER COMPLETE")
print("="*80)
print("""
NEXT STEPS:

1. Check Records Periodically:
   python view_database.py

2. Run Advanced Queries:
   python query_database.py

3. Export Records:
   python export_database.py

4. Monitor Scraper Status:
   Check GitHub Actions logs

5. View in Real-time:
   tail -f logs/scraper.log (when available)
""")
print("="*80 + "\n")
