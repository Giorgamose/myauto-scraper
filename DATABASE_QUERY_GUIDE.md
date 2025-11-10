# Database Query Guide - MyAuto Scraper

This guide shows you how to query and inspect your Turso database using various methods.

## Quick Start

### For Windows Users (Recommended)

Use the **Python script** (works on all platforms):

```bash
python query_db.py stats
python query_db.py listings
python query_db.py listing 119084515
```

Or use the **Batch script**:

```cmd
query_db.bat stats
query_db.bat listings
query_db.bat listing 119084515
```

## Installation

### Requirements

**For Python script:**
```bash
pip install tabulate python-dotenv libsql-client
```

### Setup

Make sure your `.env` or `.env.local` file contains:

```env
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-auth-token
```

## Available Commands

### View Database Structure
```bash
python query_db.py tables      # Show all tables
python query_db.py schema      # Show database schema
```

### View Statistics
```bash
python query_db.py stats       # Show database statistics
```

Output includes:
- Total listings
- Listings from last 24 hours
- Notifications sent (24h)
- Total vehicles
- Search configurations count

### View Listings
```bash
python query_db.py listings          # Show last 20 listings
python query_db.py listings 50       # Show last 50 listings
python query_db.py listing 119084515 # Show specific listing
```

### View by Category
```bash
python query_db.py by-make    # Show cars grouped by manufacturer
python query_db.py by-price   # Show cars grouped by price range
```

### View Notification Logs
```bash
python query_db.py notifications     # Show last 20 notifications
python query_db.py notifications 50  # Show last 50 notifications
```

### View Recent Activity
```bash
python query_db.py recent      # Show cars added in last 7 days
python query_db.py recent 30   # Show cars added in last 30 days
```

### View Search Configurations
```bash
python query_db.py search      # Show all search configurations
```

### Export Data
```bash
python query_db.py export                    # Export to listings_export.csv
python query_db.py export my_listings.csv    # Export to custom file
```

## Database Tables

### seen_listings
Tracks which listings have been seen and notified.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Listing ID (primary key) |
| created_at | TEXT | When first seen |
| notified | INTEGER | Notification sent (0/1) |

### vehicle_details
Complete vehicle information.

| Column | Type | Description |
|--------|------|-------------|
| listing_id | TEXT | Reference to seen_listings.id |
| make | TEXT | Car manufacturer |
| model | TEXT | Car model |
| year | INTEGER | Manufacturing year |
| price | REAL | Listed price |
| currency | TEXT | Currency (USD, GEL, EUR) |
| mileage_km | INTEGER | Kilometers |
| location | TEXT | Seller location |
| seller_name | TEXT | Seller name |

### search_configurations
Your configured searches.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Search ID |
| name | TEXT | Search name |
| vehicle_make | TEXT | Make filter |
| vehicle_model | TEXT | Model filter |
| price_from | REAL | Min price |
| price_to | REAL | Max price |
| is_active | INTEGER | Enabled (0/1) |

### notifications_sent
Log of all notifications sent.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Record ID |
| listing_id | TEXT | Which listing |
| notification_type | TEXT | Type of notification |
| sent_at | TEXT | When sent |
| success | INTEGER | Success (0/1) |

## Examples

### Find cars in price range
```bash
python query_db.py listings
# Filter manually or export and filter in Excel
```

### Export and analyze
```bash
python query_db.py export cars.csv
# Open in Excel or other tool
```

### Check database stats
```bash
python query_db.py stats
```

## Troubleshooting

**Error: Database credentials not found**
- Ensure `.env.local` or `.env` exists
- Contains TURSO_DATABASE_URL and TURSO_AUTH_TOKEN

**Error: No table named 'seen_listings'**
- Run your scraper first: `python main.py`
- This initializes the database schema

**Slow queries**
- Use LIMIT: `python query_db.py listings 10`
- Or export and filter locally

## Manual SQL Queries

Using Python directly:

```python
import os
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv('.env.local')
db = DatabaseManager(os.getenv('TURSO_DATABASE_URL'), os.getenv('TURSO_AUTH_TOKEN'))

result = db.client.execute(
    "SELECT make, model, year, price FROM vehicle_details WHERE make = 'BMW' LIMIT 10"
)
for row in result:
    print(row)
```

## Files Created

- **query_db.py** - Python script (recommended, works on all platforms)
- **query_db.bat** - Windows batch script
- **query_db.sh** - Bash script (Linux/Mac)
- **DATABASE_QUERY_GUIDE.md** - This guide
