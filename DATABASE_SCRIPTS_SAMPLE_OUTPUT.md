# Database Scripts - Sample Output Examples

This document shows exactly what each database script outputs, so you know what to expect when you run them.

---

## 1. test_db_connection.py Output

Run: `python test_db_connection.py`

### ✅ Success Output (Database is Ready)

```
======================================================================
TURSO DATABASE CONNECTION TEST
======================================================================

[STEP 1] Checking environment variables...
----------------------------------------------------------------------
[OK] TURSO_DATABASE_URL is set
     libsql://car-listings-abc123.turso.io...
[OK] TURSO_AUTH_TOKEN is set
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[STEP 2] Checking libsql_client library...
----------------------------------------------------------------------
[OK] libsql_client is installed

[STEP 3] Connecting to Turso database...
----------------------------------------------------------------------
[OK] Connected to Turso database

[STEP 4] Running test query...
----------------------------------------------------------------------
[OK] Query successful
     Records in database: 42

======================================================================
SUCCESS! YOUR SETUP IS CORRECT
======================================================================

You can now use:
  • python view_database.py       - View overview & statistics
  • python query_database.py      - Advanced filtering & search
  • python db_table_view.py       - Simple table view

Start with: python view_database.py
```

### ✅ Success Output (Empty Database - Scraper Hasn't Run Yet)

```
======================================================================
TURSO DATABASE CONNECTION TEST
======================================================================

[STEP 1] Checking environment variables...
----------------------------------------------------------------------
[OK] TURSO_DATABASE_URL is set
     libsql://car-listings-abc123.turso.io...
[OK] TURSO_AUTH_TOKEN is set
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[STEP 2] Checking libsql_client library...
----------------------------------------------------------------------
[OK] libsql_client is installed

[STEP 3] Connecting to Turso database...
----------------------------------------------------------------------
[OK] Connected to Turso database

[STEP 4] Running test query...
----------------------------------------------------------------------
[OK] Query successful (no records yet)
     The database is ready, but the scraper hasn't populated it yet.
     The scraper runs every 10 minutes and will add records soon.

======================================================================
SUCCESS! YOUR SETUP IS CORRECT
======================================================================

You can now use:
  • python view_database.py       - View overview & statistics
  • python query_database.py      - Advanced filtering & search
  • python db_table_view.py       - Simple table view

Start with: python view_database.py
```

### ❌ Failure Output (Missing Environment Variable)

```
======================================================================
TURSO DATABASE CONNECTION TEST
======================================================================

[STEP 1] Checking environment variables...
----------------------------------------------------------------------
[FAILED] TURSO_DATABASE_URL is not set

To fix this:
1. Go to https://app.turso.tech
2. Select your database 'car-listings'
3. Copy the Database URL
4. Set the environment variable:

   PowerShell: $env:TURSO_DATABASE_URL = 'your-url'
   CMD:        set TURSO_DATABASE_URL=your-url
```

---

## 2. view_database.py Output

Run: `python view_database.py`

### Example Output (With 42 Records)

```
======================================================================
MYAUTO DATABASE OVERVIEW & STATISTICS
======================================================================

[PART 1] ALL SCRAPED RECORDS
----------------------------------------------------------------------
Total records in database: 42

Latest 5 records:
┌─────────────────────────────────────────────────────────────────┐
│ ID: 987654321 | Toyota Land Cruiser Prado 2005                  │
│ Make: Toyota | Model: Land Cruiser Prado | Year: 2005          │
│ Price: 17,500 GEL | Mileage: 145,000 km                        │
│ Fuel: Diesel | Transmission: Manual                            │
│ Seller: Giorgi Beridze | Phone: +995 591 234 567               │
│ Status: Customs Cleared ✓ | Found: 2024-11-09 15:45:00        │
└─────────────────────────────────────────────────────────────────┘

│ ID: 987654320 | Toyota Land Cruiser Prado 2003                  │
│ Make: Toyota | Model: Land Cruiser Prado | Year: 2003          │
│ Price: 15,200 GEL | Mileage: 187,000 km                        │
│ Fuel: Diesel | Transmission: Manual                            │
│ Seller: Nino Shvartsman | Phone: +995 599 123 456              │
│ Status: Customs Cleared ✓ | Found: 2024-11-09 14:20:00        │
└─────────────────────────────────────────────────────────────────┘

│ ID: 987654319 | Toyota Land Cruiser Prado 2004                  │
│ Make: Toyota | Model: Land Cruiser Prado | Year: 2004          │
│ Price: 16,800 GEL | Mileage: 165,000 km                        │
│ Fuel: Diesel | Transmission: Manual                            │
│ Seller: Ana Metreveli | Phone: +995 555 789 012                │
│ Status: Customs Cleared ✓ | Found: 2024-11-09 13:15:00        │
└─────────────────────────────────────────────────────────────────┘

[PART 2] TOYOTA PRADO RECORDS (Your Search)
----------------------------------------------------------------------
Toyota Prado records found: 28 out of 42 total

Your 20 most recent Toyota Prado listings:

[1] Toyota Land Cruiser Prado 2005 (ID: 987654321)
    Year: 2005, Price: 17,500 GEL, Mileage: 145,000 km
    Fuel: Diesel, Transmission: Manual
    Seller: Giorgi Beridze - +995 591 234 567
    Found: 2024-11-09 15:45:00

[2] Toyota Land Cruiser Prado 2003 (ID: 987654320)
    Year: 2003, Price: 15,200 GEL, Mileage: 187,000 km
    Fuel: Diesel, Transmission: Manual
    Seller: Nino Shvartsman - +995 599 123 456
    Found: 2024-11-09 14:20:00

[3] Toyota Land Cruiser Prado 2004 (ID: 987654319)
    Year: 2004, Price: 16,800 GEL, Mileage: 165,000 km
    Fuel: Diesel, Transmission: Manual
    Seller: Ana Metreveli - +995 555 789 012
    Found: 2024-11-09 13:15:00

[PART 3] PRICE STATISTICS
----------------------------------------------------------------------
All Records:
  Lowest price:    12,500 GEL
  Highest price:   22,000 GEL
  Average price:   15,850 GEL
  Records: 42

Toyota Prado Only:
  Lowest price:    11,500 GEL
  Highest price:   18,900 GEL
  Average price:   15,200 GEL
  Records: 28

[PART 4] YEAR STATISTICS
----------------------------------------------------------------------
Year Distribution:
  1995: 1 record
  1998: 2 records
  2000: 3 records
  2001: 2 records
  2002: 3 records
  2003: 4 records
  2004: 3 records
  2005: 4 records
  2006: 2 records
  2007: 1 record
  2008: 2 records

[PART 5] FUEL TYPE BREAKDOWN
----------------------------------------------------------------------
Diesel: 28 records (66.7%)
Petrol: 14 records (33.3%)

[PART 6] TOP MAKES AND MODELS
----------------------------------------------------------------------
Most Common Vehicles:
  1. Toyota Land Cruiser Prado: 28 listings
  2. BMW X5: 8 listings
  3. Mercedes E-Class: 4 listings
  4. Audi Q5: 2 listings

[PART 7] DEDUPLICATION STATUS
----------------------------------------------------------------------
Unique listings tracked: 42
Duplicates prevented: 0
Database integrity: GOOD ✓

======================================================================
DATABASE SUMMARY
======================================================================
Last Updated: 2024-11-09 15:45:00
Total vehicles scraped: 42
Target (Toyota Prado): 28 (66.7%)
Other vehicles: 14 (33.3%)
Growth: Steady
Status: OPERATING NORMALLY ✓
```

---

## 3. query_database.py Output

Run: `python query_database.py`

### Menu Display

```
======================================================================
MYAUTO DATABASE QUERY TOOL
======================================================================

Select an option:

1) View All Records (Latest 10)
2) Toyota Prado Records Only
3) Filter by Price Range
4) Filter by Year Range
5) Filter by Make (Manufacturer)
6) Records Added in Last N Days
7) Lookup Specific Listing (by ID)
8) Show All Records in Database
9) Export to CSV File
0) Exit

Enter your choice (0-9):
```

### Example: Option 2 (Toyota Prado Records)

```
======================================================================
TOYOTA PRADO RECORDS - 20 MOST RECENT
======================================================================

[1] Toyota Land Cruiser Prado 2005
    Listing ID: 987654321
    Price: 17,500 GEL
    Year: 2005
    Mileage: 145,000 km
    Fuel: Diesel
    Transmission: Manual
    Seller: Giorgi Beridze
    Phone: +995 591 234 567
    Location: Tbilisi
    Found: 2024-11-09 15:45:00
    URL: https://myauto.ge/...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2] Toyota Land Cruiser Prado 2003
    Listing ID: 987654320
    Price: 15,200 GEL
    Year: 2003
    Mileage: 187,000 km
    Fuel: Diesel
    Transmission: Manual
    Seller: Nino Shvartsman
    Phone: +995 599 123 456
    Location: Gori
    Found: 2024-11-09 14:20:00
    URL: https://myauto.ge/...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[3] Toyota Land Cruiser Prado 2004
    Listing ID: 987654319
    Price: 16,800 GEL
    Year: 2004
    Mileage: 165,000 km
    Fuel: Diesel
    Transmission: Manual
    Seller: Ana Metreveli
    Phone: +995 555 789 012
    Location: Kutaisi
    Found: 2024-11-09 13:15:00
    URL: https://myauto.ge/...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

======================================================================
Total Toyota Prado records found: 28
Select an option (0-9):
```

### Example: Option 3 (Price Filter)

```
======================================================================
FILTER BY PRICE RANGE
======================================================================

Enter minimum price (GEL): 11000
Enter maximum price (GEL): 15000

Found 8 records between 11,000 and 15,000 GEL:

[1] Toyota Land Cruiser Prado 2003
    Listing ID: 987654320
    Price: 15,000 GEL ← Within range
    Year: 2003
    Mileage: 187,000 km
    Fuel: Diesel
    Seller: Nino Shvartsman - +995 599 123 456
    Found: 2024-11-09 14:20:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2] Toyota Land Cruiser Prado 2002
    Listing ID: 987654318
    Price: 12,500 GEL ← Within range
    Year: 2002
    Mileage: 195,000 km
    Fuel: Diesel
    Seller: David Kvaratskhelia - +995 591 234 567
    Found: 2024-11-09 12:30:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[3] Toyota Land Cruiser Prado 2001
    Listing ID: 987654317
    Price: 11,800 GEL ← Within range
    Year: 2001
    Mileage: 205,000 km
    Fuel: Diesel
    Seller: Tamuna Burduli - +995 555 789 012
    Found: 2024-11-09 11:45:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price Statistics for Results:
  Lowest: 11,800 GEL
  Highest: 15,000 GEL
  Average: 13,400 GEL

Select an option (0-9):
```

### Example: Option 7 (Specific Listing)

```
======================================================================
LOOKUP SPECIFIC LISTING
======================================================================

Enter listing ID: 987654321

Found listing with ID 987654321:

────────────────────────────────────────────────────────────────────
LISTING ID: 987654321
────────────────────────────────────────────────────────────────────

[TITLE]
Toyota Land Cruiser Prado 2005

[VEHICLE INFORMATION]
Make:          Toyota
Model:         Land Cruiser Prado
Year:          2005
Body Type:     SUV
Color:         Gray
Interior Color: Black

[SPECIFICATIONS]
Engine Volume: 3000 cc
Engine Power:  150 HP
Fuel Type:     Diesel
Transmission:  Manual
Drive Type:    All-Wheel Drive
Mileage:       145,000 km

[PRICING]
Price:         17,500 GEL
Currency:      GEL

[CONDITION]
Condition:     Used
Owners Count:  1
Accident History: No accidents
Customs Cleared: Yes ✓

[LOCATION]
Registration Location: Tbilisi

[SELLER INFORMATION]
Seller Name:   Giorgi Beridze
Seller Phone:  +995 591 234 567
Seller Email:  giorgi.beridze@example.com
Seller Location: Tbilisi

[LISTING DETAILS]
Posted Date:   2024-10-15
Last Updated:  2024-11-09
View Count:    45 views
Favorite Count: 8 favorites

[DESCRIPTION]
Well-maintained Toyota Prado with full service history. Recently
replaced tires and brakes. Interior in excellent condition.
Customs cleared and ready for immediate use.

[URL]
https://myauto.ge/en/listings/987654321

[METADATA]
Scraped At:    2024-11-09 15:45:00
Source:        myauto.ge
Status:        Active

────────────────────────────────────────────────────────────────────

Select an option (0-9):
```

### Example: Option 9 (CSV Export)

```
======================================================================
EXPORT TO CSV
======================================================================

Enter filename (without .csv): my_prado_listings

Exporting 42 records to my_prado_listings.csv...

✓ Successfully exported 42 records to: my_prado_listings.csv

File location: c:\Users\gmaevski\Documents\MyAuto Listening Scrapper\my_prado_listings.csv

You can now open this file in Excel, Google Sheets, or any spreadsheet application.

Select an option (0-9):
```

---

## 4. db_table_view.py Output

Run: `python db_table_view.py`

```
======================================================================
VEHICLE DETAILS TABLE VIEW
======================================================================

LISTING TABLE - LATEST 50 RECORDS
──────────────────────────────────────────────────────────────────
ID           MAKE       MODEL                  YEAR  PRICE      MILEAGE    FUEL       TRANS      SCRAPED
──────────────────────────────────────────────────────────────────
987654321    Toyota     Land Cruiser Prado     2005  17500GEL   145000km   Diesel     Manual     2024-11-09
987654320    Toyota     Land Cruiser Prado     2003  15200GEL   187000km   Diesel     Manual     2024-11-09
987654319    Toyota     Land Cruiser Prado     2004  16800GEL   165000km   Diesel     Manual     2024-11-09
987654318    Toyota     Land Cruiser Prado     2002  12500GEL   195000km   Diesel     Manual     2024-11-09
987654317    Toyota     Land Cruiser Prado     2001  11800GEL   205000km   Diesel     Manual     2024-11-09
987654316    Toyota     Land Cruiser Prado     2006  18900GEL   125000km   Diesel     Manual     2024-11-09
987654315    Toyota     Land Cruiser Prado     2007  19200GEL   115000km   Diesel     Manual     2024-11-08
987654314    Toyota     Land Cruiser Prado     2008  20000GEL   105000km   Diesel     Manual     2024-11-08
987654313    Toyota     Land Cruiser Prado     2000  13500GEL   215000km   Diesel     Manual     2024-11-08
987654312    Toyota     Land Cruiser Prado     1999  11200GEL   225000km   Diesel     Manual     2024-11-08
987654311    Toyota     Land Cruiser Prado     1998  10800GEL   235000km   Diesel     Manual     2024-11-08
987654310    BMW        X5                     2010  22000GEL   189000km   Diesel     Automatic  2024-11-08
987654309    BMW        X5                     2008  19500GEL   205000km   Petrol     Automatic  2024-11-08
987654308    Mercedes   E-Class                2012  18000GEL   165000km   Diesel     Automatic  2024-11-07
987654307    Mercedes   E-Class                2010  16500GEL   185000km   Diesel     Automatic  2024-11-07
987654306    Audi       Q5                     2015  24500GEL   85000km    Petrol     Automatic  2024-11-07
──────────────────────────────────────────────────────────────────

Total records in database: 42

VEHICLES BY MAKE
──────────────────────────────────────────────────────────────────
Toyota:    28 listings
BMW:       8 listings
Mercedes:  4 listings
Audi:      2 listings

SCRAPED TODAY: 15 records
SCRAPED THIS WEEK: 38 records

Status: ACTIVELY SCRAPING ✓
Last update: 2024-11-09 15:45:00
```

---

## Understanding the Output

### What do the numbers mean?

**Price**: Listed in Georgian Lari (GEL)
- Example: `17500GEL` = 17,500 Georgian Lari
- Your search range: 11,000 - 18,000 GEL

**Mileage**: Listed in kilometers (km)
- Example: `145000km` = 145,000 kilometers
- Each record shows odometer reading

**Year**: Model year of the vehicle
- Example: `2005` = 2005 model year
- Your search range: 1995 - 2008

**Transmission**: Manual or Automatic
- Your preference: Manual
- Only Diesel, Manual Prados match your criteria

**Fuel Type**: Type of fuel the engine uses
- Your preference: Diesel
- Database also tracks Petrol vehicles for comparison

---

## Common Patterns You'll See

### ✅ These match YOUR search criteria:
```
Toyota Land Cruiser Prado (2003-2007)
Price: 15,500 GEL
Fuel: Diesel
Transmission: Manual
Status: Customs Cleared ✓
```

### ℹ️ These DON'T match but are in database:
```
BMW X5 (2010) - Different make
Mercedes E-Class (2012) - Different make
Toyota Prado 2010 - Outside year range (too new)
Toyota Prado Automatic - Different transmission (you want Manual)
```

---

## Troubleshooting Output Issues

### "No records found"
- Scraper hasn't run yet (runs every 10 minutes)
- GitHub Actions might be disabled
- Wait and try again in 10 minutes

### "Records found but data looks incomplete"
- Some listings might have missing fields
- This is normal - not all sellers provide all info
- Scripts show "None" or empty when data is missing

### "Large number of BMW/Mercedes but expected Toyota Prado"
- Your scraper is working correctly
- It scrapes ALL results from search, but tracks your target separately
- View option 2 in query_database.py to see only Toyota Prado

---

## Next Steps After Viewing

1. **Monthly Export**: Run option 9 (Export to CSV) to save data
2. **Find Specific Cars**: Use option 3 (Price Filter) to find deals
3. **Check for Changes**: Note "Last Updated" dates to track price/listing changes
4. **Contact Sellers**: Use phone numbers in full details (option 7) to inquire

---

**Version**: 1.0.0
**Last Updated**: November 9, 2025
