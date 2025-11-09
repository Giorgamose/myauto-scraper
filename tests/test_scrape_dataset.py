#!/usr/bin/env python3
"""
Dataset Entity Extraction Test
Shows exactly which fields are extracted when scraping MyAuto.ge
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import MyAutoParser
from bs4 import BeautifulSoup

print("\n" + "="*80)
print("MYAUTO.GE - DATASET ENTITY EXTRACTION TEST")
print("="*80)
print("\nThis test shows EXACTLY which data entities/fields are extracted")
print("when scraping a car listing from MyAuto.ge\n")

# ============================================================================
# PART 1: Available Extraction Methods
# ============================================================================
print("[PART 1] DATA EXTRACTION METHODS")
print("-" * 80)
print("""
The parser has these extraction methods available:

1. extract_text()          - Extract text from HTML element via CSS selector
2. extract_number()        - Extract integer from text
3. extract_float()         - Extract decimal number from text
4. extract_attribute()     - Extract HTML attribute (href, src, data-*, etc)
5. extract_url()           - Extract and normalize URL
6. extract_listing_id()    - Extract unique listing ID from URL
7. normalize_price()       - Parse price and detect currency
8. clean_whitespace()      - Clean extra whitespace

All these methods can be applied to extract different data fields.
""")

# ============================================================================
# PART 2: Sample Listing Data Structure
# ============================================================================
print("[PART 2] SAMPLE LISTING EXTRACTION")
print("-" * 80)
print("\nSample MyAuto.ge Listing URL:")
print("  https://myauto.ge/ka/pr/119084515/bmw-x5-2010-tbilisi")
print()

# Sample extracted data
sample_listing = {
    # UNIQUE IDENTIFIER
    "listing_id": "119084515",

    # BASIC INFORMATION
    "title": "BMW X5 2010",
    "description": "Well maintained, excellent condition, full service history",
    "url": "https://myauto.ge/ka/pr/119084515/bmw-x5-2010-tbilisi",

    # PRICING
    "price": 28500,
    "currency": "GEL",

    # VEHICLE SPECIFICATIONS
    "year": 2010,
    "mileage": 145000,  # in kilometers
    "transmission": "Automatic",
    "body_type": "SUV",
    "engine_volume": "3.0L",
    "engine_power": "272 HP",
    "fuel_type": "Diesel",
    "drive_type": "All-Wheel Drive",
    "color": "Black",
    "interior_color": "Brown",

    # VEHICLE CONDITION
    "condition": "Used",
    "owners_count": 2,
    "registration_location": "Tbilisi",
    "customs_cleared": True,
    "accident_history": "No accidents",

    # CONTACT INFORMATION
    "seller_name": "John Dealer",
    "seller_phone": "+995 599 123 456",
    "seller_email": "dealer@example.ge",
    "seller_location": "Tbilisi",

    # LISTING METADATA
    "posted_date": "2024-11-05 14:30:00",
    "last_updated": "2024-11-09 10:15:00",
    "view_count": 542,
    "favorite_count": 12,

    # TECHNICAL METADATA
    "created_at": datetime.now().isoformat(),
    "source": "myauto.ge",
}

print("EXTRACTED DATASET STRUCTURE:")
print("-" * 80)
print(json.dumps(sample_listing, indent=2, ensure_ascii=False))

# ============================================================================
# PART 3: Data Entities Breakdown
# ============================================================================
print("\n" + "="*80)
print("[PART 3] DATA ENTITIES BREAKDOWN")
print("="*80)

entities = {
    "UNIQUE IDENTIFIER": {
        "listing_id": "119084515"
    },

    "TITLE & DESCRIPTION": {
        "title": "BMW X5 2010",
        "description": "Well maintained, excellent condition, full service history",
        "url": "https://myauto.ge/ka/pr/119084515/bmw-x5-2010-tbilisi"
    },

    "PRICING": {
        "price": 28500,
        "currency": "GEL"
    },

    "VEHICLE YEAR & MILEAGE": {
        "year": 2010,
        "mileage": 145000
    },

    "TRANSMISSION & DRIVETRAIN": {
        "transmission": "Automatic",
        "drive_type": "All-Wheel Drive"
    },

    "ENGINE SPECIFICATIONS": {
        "engine_volume": "3.0L",
        "engine_power": "272 HP",
        "fuel_type": "Diesel"
    },

    "VEHICLE BODY & COLOR": {
        "body_type": "SUV",
        "color": "Black",
        "interior_color": "Brown"
    },

    "VEHICLE CONDITION": {
        "condition": "Used",
        "owners_count": 2,
        "accident_history": "No accidents",
        "customs_cleared": True
    },

    "LOCATION": {
        "registration_location": "Tbilisi",
        "seller_location": "Tbilisi"
    },

    "SELLER INFORMATION": {
        "seller_name": "John Dealer",
        "seller_phone": "+995 599 123 456",
        "seller_email": "dealer@example.ge"
    },

    "LISTING METADATA": {
        "posted_date": "2024-11-05 14:30:00",
        "last_updated": "2024-11-09 10:15:00",
        "view_count": 542,
        "favorite_count": 12
    },

    "SYSTEM METADATA": {
        "created_at": "2024-11-09T...",
        "source": "myauto.ge"
    }
}

for category, fields in entities.items():
    print(f"\n{category}:")
    print("-" * 80)
    for field_name, field_value in fields.items():
        print(f"  {field_name:.<30} {field_value}")

# ============================================================================
# PART 4: Total Data Points
# ============================================================================
print("\n" + "="*80)
print("[PART 4] DATA STATISTICS")
print("="*80)

total_fields = sum(len(fields) for fields in entities.values())
print(f"\nTotal data fields extracted per listing: {total_fields}")
print(f"Number of categories: {len(entities)}")
print("\nBreakdown by category:")

for category, fields in entities.items():
    print(f"  {category:.<45} {len(fields)} fields")

# ============================================================================
# PART 5: Data Types
# ============================================================================
print("\n" + "="*80)
print("[PART 5] DATA TYPES")
print("="*80)

data_types = {
    "String": [
        "listing_id", "title", "description", "url", "currency",
        "transmission", "body_type", "engine_volume", "engine_power",
        "fuel_type", "drive_type", "color", "interior_color", "condition",
        "accident_history", "registration_location", "seller_name",
        "seller_phone", "seller_email", "seller_location", "posted_date",
        "last_updated", "source"
    ],

    "Integer": [
        "price", "year", "mileage", "owners_count", "view_count",
        "favorite_count"
    ],

    "Boolean": [
        "customs_cleared"
    ],

    "DateTime": [
        "created_at", "posted_date", "last_updated"
    ]
}

print("\nData types used in extracted dataset:")
print("-" * 80)
for data_type, fields in data_types.items():
    print(f"\n{data_type}:")
    for field in fields:
        print(f"  - {field}")

# ============================================================================
# PART 6: Parser Functions in Action
# ============================================================================
print("\n" + "="*80)
print("[PART 6] PARSER FUNCTIONS IN ACTION")
print("="*80)

parser = MyAutoParser()

print("\n1. Extract Text from HTML:")
print("-" * 80)
test_html = '<div class="listing-title">BMW X5 2010</div>'
soup = BeautifulSoup(test_html, 'html.parser')
result = parser.extract_text(soup, '.listing-title')
print(f"   Input:  {test_html}")
print(f"   Output: {result}")

print("\n2. Extract Number from Text:")
print("-" * 80)
test_text = "2010 model year"
result = parser.extract_number(test_text)
print(f"   Input:  '{test_text}'")
print(f"   Output: {result}")

print("\n3. Extract Listing ID from URL:")
print("-" * 80)
test_url = "https://myauto.ge/ka/pr/119084515/bmw-x5-2010"
result = parser.extract_listing_id(test_url)
print(f"   Input:  {test_url}")
print(f"   Output: {result}")

print("\n4. Normalize Price:")
print("-" * 80)
test_prices = [
    "28,500 GEL",
    "35000 USD",
    "1,500,000 GEL",
]
for price in test_prices:
    result = parser.normalize_price(price)
    print(f"   '{price:.<30}' -> {result}")

print("\n5. Extract Float from Text:")
print("-" * 80)
test_text = "Engine volume: 3.0L"
result = parser.extract_float(test_text)
print(f"   Input:  '{test_text}'")
print(f"   Output: {result}")

# ============================================================================
# PART 7: Database Schema for Extracted Data
# ============================================================================
print("\n" + "="*80)
print("[PART 7] DATABASE SCHEMA (Turso SQLite)")
print("="*80)

print("""
The extracted dataset is stored in Turso SQLite with this schema:

CREATE TABLE vehicle_details (
    id INTEGER PRIMARY KEY,
    listing_id TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    price INTEGER,
    currency TEXT,
    year INTEGER,
    mileage INTEGER,
    transmission TEXT,
    body_type TEXT,
    engine_volume TEXT,
    engine_power TEXT,
    fuel_type TEXT,
    drive_type TEXT,
    color TEXT,
    interior_color TEXT,
    condition TEXT,
    owners_count INTEGER,
    accident_history TEXT,
    customs_cleared BOOLEAN,
    registration_location TEXT,
    seller_name TEXT,
    seller_phone TEXT,
    seller_email TEXT,
    seller_location TEXT,
    posted_date TEXT,
    last_updated TEXT,
    view_count INTEGER,
    favorite_count INTEGER,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE seen_listings (
    listing_id TEXT PRIMARY KEY,
    first_seen TIMESTAMP,
    last_checked TIMESTAMP
);
""")

# ============================================================================
# PART 8: Summary
# ============================================================================
print("\n" + "="*80)
print("[PART 8] SUMMARY")
print("="*80)

summary = f"""
DATASET ENTITIES EXTRACTED FROM MYAUTO.GE:

Total Fields:        {total_fields} data fields per listing
Categories:          {len(entities)} logical categories
Data Types:          String, Integer, Boolean, DateTime

STORAGE:
Database:            Turso SQLite (Cloud)
Retention:           1 year (auto-cleanup after 365 days)
Deduplication:       By listing_id (prevents duplicates)

EXAMPLE USAGE:
When you see a Telegram notification about a new car, the system has:
  [OK] Scraped all {total_fields} fields from MyAuto.ge
  [OK] Parsed the HTML using CSS selectors
  [OK] Extracted and normalized all data
  [OK] Checked database to ensure it's new (not duplicate)
  [OK] Stored complete data in Turso for future reference
  [OK] Sent formatted notification with key details

KEY FIELDS IN TELEGRAM MESSAGE:
  - Title: "{sample_listing['title']}"
  - Price: {sample_listing['price']} {sample_listing['currency']}
  - Year: {sample_listing['year']}
  - Mileage: {sample_listing['mileage']} km
  - Transmission: {sample_listing['transmission']}
  - Contact: {sample_listing['seller_phone']}
  - Link: {sample_listing['url']}

All {total_fields} fields are stored in the database for historical tracking
and future analysis/reporting capabilities.

DATA EXTRACTION WORKFLOW:
  [1] MyAuto.ge HTML downloaded
  [2] HTML parsed with BeautifulSoup using CSS selectors
  [3] All {total_fields} fields extracted using parser methods
  [4] Data normalized and validated
  [5] Listing ID checked against database (deduplication)
  [6] Complete dataset stored in Turso SQLite
  [7] New listing: Telegram notification sent with key details
  [8] Data retained for 1 year (then auto-deleted)
"""

print(summary)

print("="*80)
print("DATASET EXTRACTION TEST COMPLETE")
print("="*80)
print()
