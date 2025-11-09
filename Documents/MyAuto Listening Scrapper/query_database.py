#!/usr/bin/env python3
"""
Advanced Database Query Tool
Filter and search scraped records with multiple criteria
"""

import os
import sys
from datetime import datetime, timedelta
from libsql_client import create_client_sync

# Get database credentials from environment
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
    print("\n[ERROR] Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN environment variables")
    sys.exit(1)

def connect_db():
    """Connect to Turso database"""
    try:
        client = create_client_sync(
            url=TURSO_DATABASE_URL,
            auth_token=TURSO_AUTH_TOKEN
        )
        return client
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        sys.exit(1)

def print_header(title):
    """Print section header"""
    print("\n" + "="*80)
    print(title)
    print("="*80)

def print_record(record, columns):
    """Print a single record"""
    print("\n" + "-"*80)
    for i, col_name in enumerate(columns):
        value = record[i]
        # Format value for display
        if value is None:
            value = "N/A"
        elif isinstance(value, bool):
            value = "Yes" if value else "No"
        print(f"{col_name:.<30} {value}")

# ============================================================================
# QUERY OPTIONS
# ============================================================================
print("\n" + "="*80)
print("ADVANCED DATABASE QUERY TOOL")
print("="*80)
print("\nAvailable Queries:")
print("  1. All Records (latest)")
print("  2. Toyota Prado Records")
print("  3. Filter by Price Range")
print("  4. Filter by Year Range")
print("  5. Filter by Make")
print("  6. Records Added in Last N Days")
print("  7. Specific Listing by ID")
print("  8. Show All Records (full details)")
print("  9. Export to CSV")
print("  0. Exit")

choice = input("\nSelect query (0-9): ").strip()

client = connect_db()

# ============================================================================
# QUERY 1: All Records (Latest)
# ============================================================================
if choice == "1":
    print_header("ALL RECORDS - LATEST 10")

    result = client.execute("""
        SELECT listing_id, title, make, model, year, price, currency,
               fuel_type, transmission, mileage, seller_phone, created_at
        FROM vehicle_details
        ORDER BY created_at DESC
        LIMIT 10
    """)

    if result.rows:
        columns = ["Listing ID", "Title", "Make", "Model", "Year", "Price",
                   "Currency", "Fuel", "Transmission", "Mileage", "Seller", "Scraped At"]

        print(f"\nFound {len(result.rows)} records:\n")
        for i, row in enumerate(result.rows, 1):
            print(f"[{i}] {row[1]} (ID: {row[0]})")
            print(f"    {row[2]} {row[3]} {row[4]}")
            print(f"    Price: {row[5]} {row[6]} | Fuel: {row[7]} | Trans: {row[8]}")
            print(f"    Mileage: {row[9]} km | Seller: {row[10]}")
            print(f"    Scraped: {row[11]}")
    else:
        print("\n[INFO] No records found")

# ============================================================================
# QUERY 2: Toyota Prado Records
# ============================================================================
elif choice == "2":
    print_header("TOYOTA PRADO RECORDS (YOUR SEARCH)")

    result = client.execute("""
        SELECT listing_id, title, year, price, currency, mileage,
               fuel_type, transmission, seller_name, seller_phone, created_at
        FROM vehicle_details
        WHERE make = 'Toyota' AND model = 'Land Cruiser Prado'
        ORDER BY created_at DESC
        LIMIT 20
    """)

    if result.rows:
        print(f"\nFound {len(result.rows)} Toyota Prado records:\n")
        for i, row in enumerate(result.rows, 1):
            print(f"[{i}] {row[1]} (ID: {row[0]})")
            print(f"    Year: {row[2]} | Price: {row[3]} {row[4]} | Mileage: {row[5]} km")
            print(f"    Fuel: {row[6]} | Transmission: {row[7]}")
            print(f"    Seller: {row[8]} | Phone: {row[9]}")
            print(f"    Found: {row[10]}")
            print()
    else:
        print("\n[INFO] No Toyota Prado records found in database")

# ============================================================================
# QUERY 3: Filter by Price Range
# ============================================================================
elif choice == "3":
    print_header("FILTER BY PRICE RANGE")

    try:
        price_min = int(input("Minimum price (GEL): "))
        price_max = int(input("Maximum price (GEL): "))

        result = client.execute(f"""
            SELECT listing_id, title, make, model, year, price, currency,
                   mileage, fuel_type, transmission, created_at
            FROM vehicle_details
            WHERE price >= {price_min} AND price <= {price_max}
            ORDER BY price ASC
            LIMIT 20
        """)

        if result.rows:
            print(f"\nFound {len(result.rows)} records in price range {price_min}-{price_max} GEL:\n")
            for i, row in enumerate(result.rows, 1):
                print(f"[{i}] {row[1]} (ID: {row[0]})")
                print(f"    {row[2]} {row[3]} {row[4]} | Price: {row[5]} {row[6]}")
                print(f"    Mileage: {row[7]} km | Fuel: {row[8]} | Trans: {row[9]}")
                print(f"    Found: {row[10]}")
                print()
        else:
            print(f"\n[INFO] No records in price range {price_min}-{price_max} GEL")
    except ValueError:
        print("[ERROR] Invalid price input")

# ============================================================================
# QUERY 4: Filter by Year Range
# ============================================================================
elif choice == "4":
    print_header("FILTER BY YEAR RANGE")

    try:
        year_min = int(input("From year (e.g., 1995): "))
        year_max = int(input("To year (e.g., 2008): "))

        result = client.execute(f"""
            SELECT listing_id, title, make, model, year, price, currency,
                   mileage, fuel_type, created_at
            FROM vehicle_details
            WHERE year >= {year_min} AND year <= {year_max}
            ORDER BY year DESC
            LIMIT 20
        """)

        if result.rows:
            print(f"\nFound {len(result.rows)} records from {year_min}-{year_max}:\n")
            for i, row in enumerate(result.rows, 1):
                print(f"[{i}] {row[1]} (ID: {row[0]})")
                print(f"    {row[2]} {row[3]} {row[4]} | Price: {row[5]} {row[6]}")
                print(f"    Mileage: {row[7]} km | Fuel: {row[8]}")
                print(f"    Found: {row[9]}")
                print()
        else:
            print(f"\n[INFO] No records from {year_min}-{year_max}")
    except ValueError:
        print("[ERROR] Invalid year input")

# ============================================================================
# QUERY 5: Filter by Make
# ============================================================================
elif choice == "5":
    print_header("FILTER BY MAKE")

    make = input("Enter make (e.g., Toyota, BMW, Mercedes): ").strip()

    result = client.execute(f"""
        SELECT listing_id, title, make, model, year, price, currency,
               mileage, fuel_type, created_at
        FROM vehicle_details
        WHERE make = '{make}'
        ORDER BY created_at DESC
        LIMIT 20
    """)

    if result.rows:
        print(f"\nFound {len(result.rows)} {make} records:\n")
        for i, row in enumerate(result.rows, 1):
            print(f"[{i}] {row[1]} (ID: {row[0]})")
            print(f"    {row[2]} {row[3]} {row[4]} | Price: {row[5]} {row[6]}")
            print(f"    Mileage: {row[7]} km | Fuel: {row[8]}")
            print(f"    Found: {row[9]}")
            print()
    else:
        print(f"\n[INFO] No {make} records found in database")

# ============================================================================
# QUERY 6: Records Added in Last N Days
# ============================================================================
elif choice == "6":
    print_header("RECORDS ADDED IN LAST N DAYS")

    try:
        days = int(input("Number of days: "))

        result = client.execute(f"""
            SELECT listing_id, title, make, model, year, price, currency,
                   mileage, fuel_type, created_at
            FROM vehicle_details
            WHERE created_at >= datetime('now', '-{days} days')
            ORDER BY created_at DESC
            LIMIT 20
        """)

        if result.rows:
            print(f"\nFound {len(result.rows)} records from last {days} days:\n")
            for i, row in enumerate(result.rows, 1):
                print(f"[{i}] {row[1]} (ID: {row[0]})")
                print(f"    {row[2]} {row[3]} {row[4]} | Price: {row[5]} {row[6]}")
                print(f"    Mileage: {row[7]} km | Fuel: {row[8]}")
                print(f"    Found: {row[9]}")
                print()
        else:
            print(f"\n[INFO] No records from last {days} days")
    except ValueError:
        print("[ERROR] Invalid number input")

# ============================================================================
# QUERY 7: Specific Listing by ID
# ============================================================================
elif choice == "7":
    print_header("LOOKUP SPECIFIC LISTING")

    listing_id = input("Enter listing ID: ").strip()

    result = client.execute(f"""
        SELECT listing_id, title, description, make, model, year, price,
               currency, mileage, transmission, body_type, color, fuel_type,
               condition, owners_count, accident_history, customs_cleared,
               seller_name, seller_phone, seller_email, registration_location,
               posted_date, last_updated, view_count, favorite_count, url,
               created_at
        FROM vehicle_details
        WHERE listing_id = '{listing_id}'
    """)

    if result.rows:
        row = result.rows[0]
        print(f"\nListing ID: {row[0]}")
        print("\nFull Details:")
        print("-"*80)
        print(f"Title:                  {row[1]}")
        print(f"Description:            {row[2]}")
        print(f"Make:                   {row[3]}")
        print(f"Model:                  {row[4]}")
        print(f"Year:                   {row[5]}")
        print(f"Price:                  {row[6]} {row[7]}")
        print(f"Mileage:                {row[8]} km")
        print(f"Transmission:           {row[9]}")
        print(f"Body Type:              {row[10]}")
        print(f"Color:                  {row[11]}")
        print(f"Fuel Type:              {row[12]}")
        print(f"Condition:              {row[13]}")
        print(f"Previous Owners:        {row[14]}")
        print(f"Accident History:       {row[15]}")
        print(f"Customs Cleared:        {row[16]}")
        print(f"Seller Name:            {row[17]}")
        print(f"Seller Phone:           {row[18]}")
        print(f"Seller Email:           {row[19]}")
        print(f"Location:               {row[20]}")
        print(f"Posted Date:            {row[21]}")
        print(f"Last Updated:           {row[22]}")
        print(f"Views:                  {row[23]}")
        print(f"Favorites:              {row[24]}")
        print(f"URL:                    {row[25]}")
        print(f"Scraped At:             {row[26]}")
    else:
        print(f"\n[INFO] Listing ID {listing_id} not found in database")

# ============================================================================
# QUERY 8: Show All Records
# ============================================================================
elif choice == "8":
    print_header("ALL RECORDS IN DATABASE")

    result = client.execute("""
        SELECT COUNT(*) as count FROM vehicle_details
    """)
    total = result.rows[0][0] if result.rows else 0

    print(f"\nTotal records: {total}")

    if total > 0:
        result = client.execute("""
            SELECT listing_id, title, make, model, year, price, currency,
                   mileage, fuel_type, created_at
            FROM vehicle_details
            ORDER BY created_at DESC
        """)

        print(f"\nShowing all {len(result.rows)} records:\n")
        for i, row in enumerate(result.rows, 1):
            print(f"[{i}] {row[1]} (ID: {row[0]})")
            print(f"    {row[2]} {row[3]} {row[4]} | Price: {row[5]} {row[6]}")
            print(f"    Mileage: {row[7]} km | Fuel: {row[8]} | Scraped: {row[9]}")
            print()
    else:
        print("\n[INFO] No records in database yet")

# ============================================================================
# QUERY 9: Export to CSV
# ============================================================================
elif choice == "9":
    print_header("EXPORT TO CSV")

    filename = input("Enter filename (default: export.csv): ").strip() or "export.csv"

    result = client.execute("""
        SELECT listing_id, title, make, model, year, price, currency,
               mileage, transmission, fuel_type, seller_name, seller_phone,
               registration_location, posted_date, created_at, url
        FROM vehicle_details
        ORDER BY created_at DESC
    """)

    if result.rows:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                headers = ["listing_id", "title", "make", "model", "year", "price",
                          "currency", "mileage", "transmission", "fuel_type",
                          "seller_name", "seller_phone", "location", "posted_date",
                          "scraped_at", "url"]
                f.write(",".join(headers) + "\n")

                # Write data
                for row in result.rows:
                    values = [str(v).replace(",", ";") if v else "" for v in row]
                    f.write(",".join(values) + "\n")

            print(f"\n[OK] Exported {len(result.rows)} records to {filename}")
            print(f"\nFile location: {os.path.abspath(filename)}")
        except Exception as e:
            print(f"[ERROR] Failed to export: {e}")
    else:
        print("\n[INFO] No records to export")

# ============================================================================
# EXIT
# ============================================================================
elif choice == "0":
    print("\n[OK] Exiting...")
    sys.exit(0)

else:
    print("\n[ERROR] Invalid option")
    sys.exit(1)

print("\n" + "="*80)
print("QUERY COMPLETE")
print("="*80 + "\n")
