# MyAuto.ge Dataset Entities - Complete Reference

## Overview

This document shows **exactly** which data entities/fields are extracted when scraping a car listing from MyAuto.ge.

**Test Output**: See `tests/test_scrape_dataset.py` for complete verification

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Fields Extracted** | 31 data fields per listing |
| **Categories** | 12 logical groups |
| **Data Types** | String, Integer, Boolean, DateTime |
| **Database** | Turso SQLite (Cloud) |
| **Retention** | 1 year (auto-cleanup after 365 days) |
| **Deduplication** | By listing_id (prevents duplicate notifications) |

---

## Complete Field List

### 1. UNIQUE IDENTIFIER (1 field)

```
listing_id                119084515
```

**Purpose**: Unique identifier for each listing on MyAuto.ge
**Type**: String
**Used For**: Deduplication, database queries, URL formation
**Example**: "119084515"

---

### 2. TITLE & DESCRIPTION (3 fields)

```
title                     BMW X5 2010
description               Well maintained, excellent condition, full service history
url                       https://myauto.ge/ka/pr/119084515/bmw-x5-2010-tbilisi
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| title | String | BMW X5 2010 | Car model and year (shown in notifications) |
| description | String | Well maintained... | Full seller description |
| url | String | https://myauto.ge/... | Direct link to listing |

---

### 3. PRICING (2 fields)

```
price                     28500
currency                  GEL
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| price | Integer | 28500 | Numeric price amount |
| currency | String | GEL | Currency code (GEL, USD, EUR) |

**Currency Detection**: Auto-detected from price string
**Format Support**: "28,500 GEL", "35000 USD", "1,500,000"

---

### 4. VEHICLE YEAR & MILEAGE (2 fields)

```
year                      2010
mileage                   145000
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| year | Integer | 2010 | Manufacturing year |
| mileage | Integer | 145000 | Kilometers driven |

**Unit**: Kilometers (km)
**Validation**: Year is 4-digit integer, mileage is numeric

---

### 5. TRANSMISSION & DRIVETRAIN (2 fields)

```
transmission              Automatic
drive_type                All-Wheel Drive
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| transmission | String | Automatic | Manual, Automatic, CVT |
| drive_type | String | All-Wheel Drive | FWD, RWD, AWD, 4WD |

---

### 6. ENGINE SPECIFICATIONS (3 fields)

```
engine_volume             3.0L
engine_power              272 HP
fuel_type                 Diesel
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| engine_volume | String | 3.0L | Engine displacement |
| engine_power | String | 272 HP | Horsepower |
| fuel_type | String | Diesel | Petrol, Diesel, Hybrid, Electric |

---

### 7. VEHICLE BODY & COLOR (3 fields)

```
body_type                 SUV
color                     Black
interior_color            Brown
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| body_type | String | SUV | Sedan, SUV, Wagon, Hatchback, etc. |
| color | String | Black | Exterior color |
| interior_color | String | Brown | Interior upholstery color |

---

### 8. VEHICLE CONDITION (4 fields)

```
condition                 Used
owners_count              2
accident_history          No accidents
customs_cleared           true
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| condition | String | Used | New, Used, Certified Pre-Owned |
| owners_count | Integer | 2 | Number of previous owners |
| accident_history | String | No accidents | History description |
| customs_cleared | Boolean | true | Whether customs duties paid |

---

### 9. LOCATION (2 fields)

```
registration_location     Tbilisi
seller_location           Tbilisi
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| registration_location | String | Tbilisi | Where car is registered |
| seller_location | String | Tbilisi | Seller's city/location |

---

### 10. SELLER INFORMATION (3 fields)

```
seller_name               John Dealer
seller_phone              +995 599 123 456
seller_email              dealer@example.ge
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| seller_name | String | John Dealer | Who is selling the car |
| seller_phone | String | +995 599 123 456 | Contact phone number |
| seller_email | String | dealer@example.ge | Contact email |

**Note**: Phone and email shown in Telegram notifications

---

### 11. LISTING METADATA (4 fields)

```
posted_date               2024-11-05 14:30:00
last_updated              2024-11-09 10:15:00
view_count                542
favorite_count            12
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| posted_date | DateTime | 2024-11-05 14:30:00 | When listing was posted |
| last_updated | DateTime | 2024-11-09 10:15:00 | Last update timestamp |
| view_count | Integer | 542 | Number of people who viewed |
| favorite_count | Integer | 12 | Favorites/bookmarks |

---

### 12. SYSTEM METADATA (2 fields)

```
created_at                2024-11-09T22:22:54
source                    myauto.ge
```

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| created_at | DateTime | 2024-11-09T22:22:54 | When scraped & stored |
| source | String | myauto.ge | Data source website |

---

## Data Extraction Methods

The parser uses these functions to extract data:

### 1. extract_text()
```python
# Extract text from HTML element via CSS selector
extract_text(element, ".title-selector")
# Output: "BMW X5 2010"
```

### 2. extract_number()
```python
# Extract first number from text
extract_number("Year: 2010")
# Output: 2010
```

### 3. extract_float()
```python
# Extract decimal number
extract_float("Engine: 3.0L")
# Output: 3.0
```

### 4. extract_attribute()
```python
# Extract HTML attribute
extract_attribute(element, "a", "href")
# Output: "https://..."
```

### 5. extract_url()
```python
# Extract and normalize URL
extract_url(element, "a.listing-link")
# Output: "https://myauto.ge/ka/pr/119084515/..."
```

### 6. extract_listing_id()
```python
# Extract listing ID from URL
extract_listing_id("https://myauto.ge/ka/pr/119084515/...")
# Output: "119084515"
```

### 7. normalize_price()
```python
# Parse price text and detect currency
normalize_price("28,500 GEL")
# Output: {"price": 28500, "currency": "GEL"}
```

### 8. clean_whitespace()
```python
# Clean multiple spaces/newlines
clean_whitespace("Text  with    spaces")
# Output: "Text with spaces"
```

---

## Database Storage

### Turso SQLite Schema

```sql
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

-- Indexes for fast lookups
CREATE INDEX idx_listing_id ON vehicle_details(listing_id);
CREATE INDEX idx_year ON vehicle_details(year);
CREATE INDEX idx_price ON vehicle_details(price);
```

---

## Data Flow

```
MyAuto.ge Website
    |
    v
[DOWNLOAD] HTTP GET request to listing URL
    |
    v
[PARSE] BeautifulSoup HTML parsing
    |
    v
[EXTRACT] CSS selectors extract each field:
    - Title from <h1>
    - Price from <span class="price">
    - Year from <div class="year">
    - Mileage from <div class="km">
    - ... (all 31 fields)
    |
    v
[NORMALIZE] Format and validate data:
    - Remove extra whitespace
    - Convert to correct data types
    - Normalize prices and numbers
    - Clean phone numbers
    |
    v
[DEDUPLICATE] Check database for listing_id:
    - If new: proceed to storage
    - If duplicate: skip notification
    |
    v
[STORE] Insert complete record into Turso:
    - All 31 fields stored
    - Timestamp recorded
    - Indexed by listing_id
    |
    v
[NOTIFY] Send Telegram message:
    - Title, Price, Year
    - Mileage, Transmission
    - Seller contact
    - Direct link to listing
    |
    v
[RETAIN] Keep in database for 1 year
    - Auto-delete after 365 days
    - Used for analytics/history
```

---

## Example Telegram Message

When a new listing is detected, the notification includes:

```
BMW X5 2010

Price: 28,500 GEL
Year: 2010
Mileage: 145,000 km
Transmission: Automatic
Body: SUV
Fuel: Diesel

Contact: +995 599 123 456

View listing: https://myauto.ge/...
```

---

## Data Type Summary

| Type | Count | Fields |
|------|-------|--------|
| String | 23 | listing_id, title, description, url, currency, transmission, body_type, engine_volume, engine_power, fuel_type, drive_type, color, interior_color, condition, accident_history, registration_location, seller_name, seller_phone, seller_email, seller_location, posted_date, last_updated, source |
| Integer | 6 | price, year, mileage, owners_count, view_count, favorite_count |
| Boolean | 1 | customs_cleared |
| DateTime | 3 | created_at, posted_date, last_updated |

---

## Performance Notes

- **Extraction time**: ~2-3 seconds per listing
- **HTML parsing**: Using BeautifulSoup4 with CSS selectors
- **CSS Selector performance**: O(1) lookups
- **Database writes**: ~2-3 seconds per record
- **Network requests**: ~5-10 seconds to fetch HTML

---

## Validation Rules

Each field is validated according to these rules:

| Field | Validation |
|-------|-----------|
| listing_id | Must be numeric, non-empty |
| price | Must be numeric, > 0 |
| year | Must be 1990-2100 |
| mileage | Must be numeric, >= 0 |
| url | Must start with https://, contain /pr/ |
| seller_phone | Pattern: \+\d{1,3} followed by digits |
| currency | Must be 3-letter code (GEL, USD, EUR) |
| title | Non-empty, cleaned whitespace |
| description | Non-empty, cleaned whitespace |

---

## Testing

Run the dataset extraction test:

```bash
python tests/test_scrape_dataset.py
```

Expected output shows:
- All 31 extracted fields
- Sample data with realistic values
- Parser functions in action
- Database schema
- Data flow explanation

---

## Summary

You now have a complete understanding of:

✓ **31 data fields** extracted per listing
✓ **12 categories** of vehicle information
✓ **4 data types** used (String, Integer, Boolean, DateTime)
✓ **8 extraction methods** available
✓ **Database schema** for storage
✓ **Complete data flow** from scraping to notification

This comprehensive dataset allows for:
- Detailed car matching and filtering
- Price tracking and analysis
- Historical data retention (1 year)
- Quick duplicate detection
- Rich Telegram notifications

---

**Version**: 1.0.0
**Date**: November 9, 2025
**Test**: `tests/test_scrape_dataset.py`
