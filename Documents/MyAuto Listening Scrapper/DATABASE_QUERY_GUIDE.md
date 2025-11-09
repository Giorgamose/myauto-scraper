# Database Query & Viewer Guide

Learn how to query and view your scraped car listings from Turso SQLite database.

---

## Overview

Three powerful scripts to view your scraped records:

1. **view_database.py** - Overview dashboard with statistics
2. **query_database.py** - Advanced filtering and searching
3. **db_table_view.py** - Simple table view of records

---

## Before You Start

### Set Environment Variables

You need to set these environment variables first:

**On Windows (PowerShell):**
```powershell
$env:TURSO_DATABASE_URL = "libsql://your-db.turso.io"
$env:TURSO_AUTH_TOKEN = "your-token-here"
```

**On Windows (Command Prompt):**
```cmd
set TURSO_DATABASE_URL=libsql://your-db.turso.io
set TURSO_AUTH_TOKEN=your-token-here
```

**On Mac/Linux:**
```bash
export TURSO_DATABASE_URL="libsql://your-db.turso.io"
export TURSO_AUTH_TOKEN="your-token-here"
```

### Where to Get Credentials

1. Go to https://app.turso.tech
2. Select your database "car-listings"
3. Copy the Database URL
4. Generate/copy your Auth Token

---

## Script 1: View Database Overview

### Purpose
Quick overview of all data in your database with statistics

### Run
```bash
python view_database.py
```

### Output Shows
- Total records in database
- Sample of latest 5 records
- Toyota Prado records (your search)
- Price statistics (min, max, average)
- Year statistics
- Fuel type breakdown
- Top makes and models
- Deduplication status

### Example Output
```
[PART 1] ALL SCRAPED RECORDS
Total records in database: 42

[PART 2] SAMPLE RECORDS (Latest 5)
Latest 5 records:

Listing ID:     456789012
Title:          Toyota Land Cruiser Prado 2003
Make:           Toyota
Model:          Land Cruiser Prado
Year:           2003
Price:          15,500 GEL
...

[PART 3] TOYOTA PRADO RECORDS (Your Search)
Toyota Prado records: 15

Toyota Prado listings found:

[1] Toyota Land Cruiser Prado 2003 (ID: 456789012)
    Year: 2003, Price: 15,500 GEL, Mileage: 187,000 km
    Fuel: Diesel, Transmission: Manual
    Seller: Giorgi Beridze - +995 591 234 567
    Found: 2024-11-08 09:30:00
```

---

## Script 2: Advanced Query Tool

### Purpose
Filter and search records with multiple criteria

### Run
```bash
python query_database.py
```

### Menu Options

**Option 1: All Records (Latest)**
- Shows latest 10 records
- Full details for each
- Perfect for seeing what's new

**Option 2: Toyota Prado Records**
- Shows only your Toyota Prado search results
- Displays your 20 most recent finds
- Great for monitoring your specific search

**Option 3: Filter by Price Range**
```
Enter minimum price: 11000
Enter maximum price: 18000
```
Shows all records within price range

**Option 4: Filter by Year Range**
```
Enter from year: 1995
Enter to year: 2008
```
Shows records from specific years

**Option 5: Filter by Make**
```
Enter make: Toyota
```
Shows all vehicles of a specific make

**Option 6: Records Added in Last N Days**
```
Enter number of days: 7
```
Shows records scraped in the last week

**Option 7: Lookup Specific Listing**
```
Enter listing ID: 456789012
```
Shows complete details for one listing (all 31 fields!)

**Option 8: Show All Records**
- Displays every record in database
- Full details
- Use if you need to see everything

**Option 9: Export to CSV**
```
Enter filename: my_cars.csv
```
Exports all records to CSV file for Excel/analysis

---

## Script 3: Table View

### Purpose
Simple table format - easy to scan multiple records at once

### Run
```bash
python db_table_view.py
```

### Display Format
```
VEHICLE DETAILS TABLE
--------
ID           MAKE       MODEL                YEAR  PRICE      MILEAGE    FUEL       TRANS      SCRAPED
--------
456789012    Toyota     Land Cruiser Prado   2003  15500GEL   187000km   Diesel     Manual     2024-11-08
457890123    Toyota     Land Cruiser Prado   2005  16000GEL   165000km   Diesel     Manual     2024-11-07
...
--------

Total records: 42

Records by Make:
  Toyota: 15
  BMW: 10
  Mercedes: 8
  ...
```

---

## Quick Examples

### View All Toyota Prado Records
```bash
python query_database.py
# Select option 2
```

### Find Cars Under 15,000 GEL
```bash
python query_database.py
# Select option 3
# Min: 0
# Max: 15000
```

### See What Was Added Yesterday
```bash
python query_database.py
# Select option 6
# Days: 1
```

### Get Full Details of a Listing
```bash
python query_database.py
# Select option 7
# Listing ID: 456789012
```

### Export All Records to Excel
```bash
python query_database.py
# Select option 9
# Filename: my_cars.csv
# Open in Excel
```

### Quick Table View
```bash
python db_table_view.py
# Shows 50 latest records in table format
```

---

## Data Available Per Record

Each listing has 31 fields stored:

### Identification
- listing_id
- title
- description
- url

### Vehicle Info
- make
- model
- year
- body_type
- color
- interior_color

### Specifications
- engine_volume
- engine_power
- fuel_type
- transmission
- drive_type
- mileage

### Pricing
- price
- currency

### Condition
- condition
- owners_count
- accident_history
- customs_cleared

### Location
- registration_location

### Seller Info
- seller_name
- seller_phone
- seller_email
- seller_location

### Metadata
- posted_date
- last_updated
- view_count
- favorite_count
- created_at (when scraped)
- source (myauto.ge)

---

## Troubleshooting

### Error: "Missing TURSO_DATABASE_URL"
**Solution**: Set environment variables
```powershell
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"
```

### Error: "Failed to connect to database"
**Solution**:
1. Check URL and token are correct
2. Verify internet connection
3. Check database exists in turso.tech dashboard
4. Try reconnecting

### No Records Found
**Solution**:
- Scraper hasn't run yet (runs every 10 minutes)
- Or no matches found for your search criteria
- Wait 10 minutes and check again

### CSV Export Creates Empty File
**Solution**:
- Check if there are any records (run view_database.py first)
- Verify file permissions
- Try different filename

---

## Database Structure

### Tables

#### vehicle_details
Main table with all 31 fields per listing

```sql
CREATE TABLE vehicle_details (
    id INTEGER PRIMARY KEY,
    listing_id TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    price INTEGER,
    currency TEXT,
    make TEXT,
    model TEXT,
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
```

#### seen_listings
Tracks unique listing IDs for deduplication

```sql
CREATE TABLE seen_listings (
    listing_id TEXT PRIMARY KEY,
    first_seen TIMESTAMP,
    last_checked TIMESTAMP
);
```

---

## Tips & Tricks

### Monitor Your Search
Run this daily to see new Toyota Prado listings:
```bash
python query_database.py
# Option 2: Toyota Prado Records
```

### Find Best Deals
```bash
python query_database.py
# Option 3: Filter by Price
# Min: 0, Max: 12000
# Shows cheapest Toyota Prado listings
```

### Track Specific Car
If you found a car but need full details:
```bash
python query_database.py
# Option 7: Lookup by ID
# Paste the listing ID
# See all 31 fields
```

### Build Spreadsheet
```bash
python query_database.py
# Option 9: Export to CSV
# Open in Excel
# Create pivot tables, charts, analysis
```

### Regular Backup
```bash
python query_database.py
# Option 9: Export to CSV
# Save with date: export_2024-11-09.csv
# Keep weekly backups
```

---

## Expected Data Growth

| Time | Records | Toyota Prado | Other Makes |
|------|---------|--------------|-------------|
| Day 1 | 5-10 | 2-3 | 3-7 |
| Day 7 | 40-70 | 15-25 | 25-45 |
| Day 30 | 200-300 | 50-100 | 150-200 |
| Day 365 | 2000-3000 | 500-800 | 1500-2200 |

Note: Exact numbers depend on how many listings match your search criteria

---

## Scheduled Viewing

Recommended schedule to monitor your scraper:

### Daily (Morning)
```bash
python db_table_view.py
```
Quick check of latest records

### Weekly (Every Sunday)
```bash
python view_database.py
```
Full statistics and summary

### Monthly (1st of month)
```bash
python query_database.py
# Option 9: Export to CSV
```
Archive monthly data

### When Needed
```bash
python query_database.py
# Various filtering options
```
Search for specific listings

---

## Support

If scripts don't work:

1. **Check environment variables** are set correctly
2. **Verify Turso credentials** in turso.tech
3. **Ensure internet connection** is working
4. **Check database exists** and has data (run scraper first)
5. **Review error messages** carefully

---

**Version**: 1.0.0
**Date**: November 9, 2025
**Scripts**: view_database.py, query_database.py, db_table_view.py
