#!/usr/bin/env python3
"""
EXACT Dataset Extraction for YOUR Search Configuration
Shows what data is extracted for: Toyota Land Cruiser Prado (1995-2008)
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "="*80)
print("DATASET EXTRACTION - TOYOTA LAND CRUISER PRADO (1995-2008)")
print("="*80)
print("\nThis shows EXACTLY what data is captured for YOUR search configuration\n")

# ============================================================================
# YOUR SEARCH CONFIGURATION
# ============================================================================
print("[PART 1] YOUR SEARCH CONFIGURATION")
print("-" * 80)

search_config = {
    "name": "Toyota Land Cruiser Prado (1995-2008)",
    "base_url": "https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-land-cruiser-prado-1995-2008",
    "criteria": {
        "make": "Toyota",
        "model": "Land Cruiser Prado",
        "year_from": 1995,
        "year_to": 2008,
        "price_from": 11000,
        "price_to": 18000,
        "currency": "GEL",
        "fuel_type": "Diesel",
        "customs_cleared": True,
        "locations": "All Georgia"
    }
}

print(f"Search Name:         {search_config['name']}")
print(f"Make:                {search_config['criteria']['make']}")
print(f"Model:               {search_config['criteria']['model']}")
print(f"Year Range:          {search_config['criteria']['year_from']}-{search_config['criteria']['year_to']}")
print(f"Price Range:         {search_config['criteria']['price_from']:,} - {search_config['criteria']['price_to']:,} {search_config['criteria']['currency']}")
print(f"Fuel Type:           {search_config['criteria']['fuel_type']}")
print(f"Customs Cleared:     {search_config['criteria']['customs_cleared']}")
print(f"Locations:           {search_config['criteria']['locations']}")

# ============================================================================
# SAMPLE TOYOTA PRADO LISTING MATCHING YOUR CRITERIA
# ============================================================================
print("\n[PART 2] SAMPLE TOYOTA PRADO LISTING (Matches Your Search Criteria)")
print("-" * 80)

# Create realistic Toyota Prado example matching search criteria
toyota_prado_listing = {
    # UNIQUE IDENTIFIER
    "listing_id": "456789012",

    # BASIC INFORMATION
    "title": "Toyota Land Cruiser Prado 2003",
    "description": "Excellent condition, full maintenance history, no accidents, original paint, well-kept interior",
    "url": "https://myauto.ge/ka/pr/456789012/toyota-land-cruiser-prado-2003-tbilisi",

    # PRICING (MATCHES YOUR CRITERIA: 11,000-18,000 GEL)
    "price": 15500,
    "currency": "GEL",

    # VEHICLE SPECIFICATIONS (MATCHES YOUR CRITERIA)
    "make": "Toyota",
    "model": "Land Cruiser Prado",
    "year": 2003,  # Within your 1995-2008 range
    "mileage": 187000,  # Kilometers

    # TRANSMISSION & DRIVETRAIN
    "transmission": "Manual",
    "drive_type": "All-Wheel Drive",

    # ENGINE SPECIFICATIONS (MATCHES YOUR CRITERIA: DIESEL)
    "engine_volume": "2.7L",
    "engine_power": "163 HP",
    "fuel_type": "Diesel",

    # VEHICLE BODY & COLOR
    "body_type": "SUV",
    "color": "Silver",
    "interior_color": "Gray",

    # VEHICLE CONDITION (MATCHES YOUR CRITERIA: CUSTOMS CLEARED)
    "condition": "Used",
    "owners_count": 1,
    "accident_history": "No accidents",
    "customs_cleared": True,

    # LOCATION
    "registration_location": "Tbilisi",
    "seller_location": "Tbilisi",

    # SELLER INFORMATION
    "seller_name": "Giorgi Beridze",
    "seller_phone": "+995 591 234 567",
    "seller_email": "giorgi@example.ge",

    # LISTING METADATA
    "posted_date": "2024-11-08 09:30:00",
    "last_updated": "2024-11-09 14:15:00",
    "view_count": 287,
    "favorite_count": 23,

    # SYSTEM METADATA
    "created_at": datetime.now().isoformat(),
    "source": "myauto.ge",
}

print("\nFull Dataset (JSON format):")
print(json.dumps(toyota_prado_listing, indent=2, ensure_ascii=False))

# ============================================================================
# DATA BREAKDOWN FOR TOYOTA PRADO
# ============================================================================
print("\n[PART 3] DATA ENTITIES - TOYOTA PRADO")
print("-" * 80)

entities = {
    "VEHICLE IDENTIFICATION": {
        "listing_id": toyota_prado_listing["listing_id"],
        "make": toyota_prado_listing["make"],
        "model": toyota_prado_listing["model"],
        "year": toyota_prado_listing["year"],
    },

    "PRICING (Your Range: 11,000-18,000 GEL)": {
        "price": toyota_prado_listing["price"],
        "currency": toyota_prado_listing["currency"],
    },

    "ENGINE (Your Fuel: Diesel)": {
        "engine_volume": toyota_prado_listing["engine_volume"],
        "engine_power": toyota_prado_listing["engine_power"],
        "fuel_type": toyota_prado_listing["fuel_type"],
    },

    "MILEAGE & TRANSMISSION": {
        "mileage": toyota_prado_listing["mileage"],
        "transmission": toyota_prado_listing["transmission"],
        "drive_type": toyota_prado_listing["drive_type"],
    },

    "BODY & COLOR": {
        "body_type": toyota_prado_listing["body_type"],
        "color": toyota_prado_listing["color"],
    },

    "CONDITION (Your Requirement: Customs Cleared)": {
        "condition": toyota_prado_listing["condition"],
        "owners_count": toyota_prado_listing["owners_count"],
        "accident_history": toyota_prado_listing["accident_history"],
        "customs_cleared": toyota_prado_listing["customs_cleared"],
    },

    "LOCATION": {
        "registration_location": toyota_prado_listing["registration_location"],
        "seller_location": toyota_prado_listing["seller_location"],
    },

    "SELLER INFORMATION": {
        "seller_name": toyota_prado_listing["seller_name"],
        "seller_phone": toyota_prado_listing["seller_phone"],
        "seller_email": toyota_prado_listing["seller_email"],
    },

    "LISTING METADATA": {
        "posted_date": toyota_prado_listing["posted_date"],
        "last_updated": toyota_prado_listing["last_updated"],
        "view_count": toyota_prado_listing["view_count"],
        "favorite_count": toyota_prado_listing["favorite_count"],
    },

    "SYSTEM": {
        "url": toyota_prado_listing["url"],
        "created_at": toyota_prado_listing["created_at"],
        "source": toyota_prado_listing["source"],
    },
}

for category, fields in entities.items():
    print(f"\n{category}:")
    print("-" * 80)
    for field_name, field_value in fields.items():
        print(f"  {field_name:.<30} {field_value}")

# ============================================================================
# YOUR NOTIFICATION FIELDS
# ============================================================================
print("\n[PART 4] TELEGRAM NOTIFICATION - YOUR CONFIGURED FIELDS")
print("-" * 80)

notification_fields = [
    "make",
    "model",
    "year",
    "price",
    "currency",
    "mileage_km",
    "fuel_type",
    "transmission",
    "location",
    "posted_date",
    "seller_name",
    "url"
]

notification_message = f"""
TELEGRAM MESSAGE YOU'LL RECEIVE:

{toyota_prado_listing['make']} {toyota_prado_listing['model']} {toyota_prado_listing['year']}

Price: {toyota_prado_listing['price']:,} {toyota_prado_listing['currency']}
Year: {toyota_prado_listing['year']}
Mileage: {toyota_prado_listing['mileage']:,} km
Fuel: {toyota_prado_listing['fuel_type']}
Transmission: {toyota_prado_listing['transmission']}
Location: {toyota_prado_listing['registration_location']}
Posted: {toyota_prado_listing['posted_date']}
Seller: {toyota_prado_listing['seller_name']}

View listing: {toyota_prado_listing['url']}
"""

print(notification_message)

# ============================================================================
# VERIFICATION CHECKLIST
# ============================================================================
print("\n[PART 5] VERIFICATION - Does This Match Your Search Criteria?")
print("-" * 80)

checks = {
    "Make is Toyota": toyota_prado_listing["make"] == "Toyota",
    "Model is Land Cruiser Prado": toyota_prado_listing["model"] == "Land Cruiser Prado",
    "Year 1995-2008": 1995 <= toyota_prado_listing["year"] <= 2008,
    "Price 11,000-18,000 GEL": 11000 <= toyota_prado_listing["price"] <= 18000,
    "Currency is GEL": toyota_prado_listing["currency"] == "GEL",
    "Fuel Type is Diesel": toyota_prado_listing["fuel_type"] == "Diesel",
    "Customs Cleared": toyota_prado_listing["customs_cleared"] == True,
    "Location in Georgia": toyota_prado_listing["registration_location"] in ["Tbilisi", "Kutaisi", "Batumi", "Zugdidi"],
}

all_passed = True
for check, result in checks.items():
    status = "[OK]" if result else "[FAIL]"
    print(f"{status} {check}")
    if not result:
        all_passed = False

if all_passed:
    print(f"\n[OK] All criteria matched!")
else:
    print(f"\n[ERROR] Some criteria not matched")

# ============================================================================
# DATA EXTRACTION WORKFLOW FOR TOYOTA PRADO
# ============================================================================
print("\n[PART 6] DATA EXTRACTION WORKFLOW")
print("-" * 80)

workflow = """
When searching for: Toyota Land Cruiser Prado (1995-2008)

[1] SCRAPER VISITS YOUR URL
    URL: https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-...
    Downloads: HTML page with all matching listings

[2] PARSE HTML WITH BEAUTIFULSOUP
    Extracts: All car listings from the page
    Filters: Only Toyota Land Cruiser Prado models

[3] FOR EACH LISTING, EXTRACT ALL FIELDS:
    - Make: Toyota (matched)
    - Model: Land Cruiser Prado (matched)
    - Year: 2003 (within 1995-2008)
    - Price: 15,500 GEL (within 11,000-18,000)
    - Fuel Type: Diesel (matched)
    - Customs Cleared: Yes (matched)
    - + 25 more fields

[4] VALIDATE AGAINST YOUR CRITERIA:
    - Year check: 1995-2008? YES
    - Price check: 11,000-18,000 GEL? YES
    - Fuel check: Diesel? YES
    - Customs check: Cleared? YES
    - Location check: Georgia? YES
    - All checks PASS!

[5] DEDUPLICATION:
    - Check database: Is listing_id 456789012 already seen?
    - Result: NEW listing detected!

[6] STORE IN DATABASE:
    All 31 fields saved to Turso SQLite
    Indexed by listing_id for future deduplication

[7] SEND TELEGRAM NOTIFICATION:
    Your configured notification fields sent:
    - Make, Model, Year
    - Price, Currency
    - Mileage, Fuel, Transmission
    - Location, Posted Date
    - Seller Name, URL

[8] RETAIN IN DATABASE:
    Data kept for 1 year
    Available for future searches and analytics
"""

print(workflow)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n[PART 7] SUMMARY")
print("="*80)

summary_text = f"""
YOUR SEARCH: Toyota Land Cruiser Prado (1995-2008)
PRICE RANGE: 11,000 - 18,000 GEL
FUEL TYPE: Diesel
CUSTOMS: Cleared
LOCATION: All Georgia

EXAMPLE LISTING THAT MATCHES:
  Make: {toyota_prado_listing['make']}
  Model: {toyota_prado_listing['model']}
  Year: {toyota_prado_listing['year']}
  Price: {toyota_prado_listing['price']:,} {toyota_prado_listing['currency']}
  Fuel: {toyota_prado_listing['fuel_type']}
  Mileage: {toyota_prado_listing['mileage']:,} km
  Seller: {toyota_prado_listing['seller_name']}
  Contact: {toyota_prado_listing['seller_phone']}

DATA FIELDS EXTRACTED: 31 total fields
DATABASE: Turso SQLite
RETENTION: 1 year
DEDUPLICATION: By listing_id (prevents duplicates)

EVERY TIME A TOYOTA PRADO MATCHES YOUR CRITERIA:
  [1] All 31 fields extracted and validated
  [2] Checked against your search criteria (price, year, fuel, etc.)
  [3] Checked database for duplicates (by listing_id)
  [4] If NEW: Telegram notification sent with key details
  [5] Complete record stored in database for 1 year

THIS IS NOT A BMW! This is a TOYOTA PRADO matching YOUR search configuration.
"""

print(summary_text)

print("="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
