#!/usr/bin/env python3
"""
Database Table View - Display records in table format
Simple, easy-to-read table of all scraped records
"""

import os
import sys
from libsql_client import create_client_sync

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
    print("\n[ERROR] Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN")
    print("\nSet environment variables:")
    print("  export TURSO_DATABASE_URL=libsql://your-db.turso.io")
    print("  export TURSO_AUTH_TOKEN=your-token-here")
    sys.exit(1)

print("\n" + "="*100)
print("DATABASE TABLE VIEW")
print("="*100)

try:
    client = create_client_sync(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )
    print("\n[OK] Connected to database\n")

except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    sys.exit(1)

# Get all records
result = client.execute("""
    SELECT listing_id, make, model, year, price, currency, mileage,
           fuel_type, transmission, seller_name, created_at
    FROM vehicle_details
    ORDER BY created_at DESC
    LIMIT 50
""")

if not result.rows:
    print("[INFO] No records in database yet\n")
    print("The scraper will populate the database as it finds matching listings.")
    print("Check back after the scraper has run (every 10 minutes).\n")
    sys.exit(0)

# Print table header
print("VEHICLE DETAILS TABLE")
print("-" * 100)
print(f"{'ID':<12} {'MAKE':<10} {'MODEL':<20} {'YEAR':<6} {'PRICE':<10} {'MILEAGE':<10} {'FUEL':<10} {'TRANS':<10} {'SCRAPED':<19}")
print("-" * 100)

# Print rows
for row in result.rows:
    listing_id = str(row[0])[:11]
    make = str(row[1])[:9] if row[1] else ""
    model = str(row[2])[:19] if row[2] else ""
    year = str(row[3])[:5] if row[3] else ""
    price = f"{row[4]}{row[5]}" if row[4] and row[5] else ""
    mileage = f"{row[6]}km" if row[6] else ""
    fuel = str(row[7])[:9] if row[7] else ""
    trans = str(row[8])[:9] if row[8] else ""
    created = str(row[10])[:19] if row[10] else ""

    print(f"{listing_id:<12} {make:<10} {model:<20} {year:<6} {price:<10} {mileage:<10} {fuel:<10} {trans:<10} {created:<19}")

# Statistics
print("-" * 100)
print(f"\nTotal records: {len(result.rows)}")

# Count by make
result = client.execute("""
    SELECT make, COUNT(*) as count
    FROM vehicle_details
    GROUP BY make
    ORDER BY count DESC
""")

if result.rows:
    print("\nRecords by Make:")
    for row in result.rows:
        print(f"  {row[0]}: {row[1]}")

print("\n" + "="*100 + "\n")
