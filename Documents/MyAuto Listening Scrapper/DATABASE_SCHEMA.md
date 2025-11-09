# Database Schema - MyAuto Car Listing Scraper

**Database:** Turso (SQLite)
**Retention:** 1 year
**Purpose:** Track car listings and send notifications only for new ones

---

## Schema Overview

This database stores:
1. **seen_listings** - All listing IDs we've tracked (deduplication)
2. **vehicle_details** - Complete vehicle information
3. **search_configurations** - Your saved search URLs
4. **notifications_sent** - History of notifications sent

---

## Complete Schema with SQL

### Table 1: seen_listings

```sql
CREATE TABLE IF NOT EXISTS seen_listings (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_notified_at TIMESTAMP,
    notified BOOLEAN DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_seen_listings_created_at
ON seen_listings(created_at);
```

**Purpose:** Quick deduplication check - if ID exists here, we've already notified about it

**Fields:**
- `id` - Listing ID from MyAuto.ge (e.g., "119084515")
- `created_at` - When we first discovered this listing
- `last_notified_at` - When we sent the WhatsApp notification
- `notified` - Always 1 (used for future features like "notify again" option)

**Usage:**
```sql
-- Check if we've seen this listing before
SELECT * FROM seen_listings WHERE id = '119084515';

-- If NULL, it's NEW → fetch details and send notification
-- If EXISTS, it's OLD → skip it
```

---

### Table 2: vehicle_details

```sql
CREATE TABLE IF NOT EXISTS vehicle_details (
    listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,

    -- VEHICLE IDENTIFICATION
    make TEXT,
    make_id INTEGER,
    model TEXT,
    model_id INTEGER,
    modification TEXT,
    year INTEGER,
    vin TEXT UNIQUE,

    -- PHYSICAL CHARACTERISTICS
    body_type TEXT,
    color TEXT,
    interior_color TEXT,
    doors INTEGER,
    seats INTEGER,
    wheel_position TEXT,
    drive_type TEXT,

    -- ENGINE INFORMATION
    fuel_type TEXT,
    fuel_type_id INTEGER,
    displacement_liters REAL,
    transmission TEXT,
    power_hp INTEGER,
    cylinders INTEGER,

    -- CONDITION
    status TEXT,
    mileage_km INTEGER,
    mileage_unit TEXT,
    customs_cleared BOOLEAN,
    technical_inspection_passed BOOLEAN,
    condition_description TEXT,

    -- PRICING
    price REAL,
    currency TEXT,
    currency_id INTEGER,
    negotiable BOOLEAN,
    installment_available BOOLEAN,
    exchange_possible BOOLEAN,

    -- SELLER INFORMATION
    seller_type TEXT,
    seller_name TEXT,
    seller_phone TEXT,
    location TEXT,
    location_id INTEGER,
    is_dealer BOOLEAN,
    dealer_id INTEGER,

    -- MEDIA
    primary_image_url TEXT,
    photo_count INTEGER,
    video_url TEXT,

    -- METADATA
    posted_date TIMESTAMP,
    last_updated TIMESTAMP,
    url TEXT,
    view_count INTEGER,
    is_vip BOOLEAN,
    is_featured BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_vehicle_details_year
ON vehicle_details(year);

CREATE INDEX IF NOT EXISTS idx_vehicle_details_price
ON vehicle_details(price);

CREATE INDEX IF NOT EXISTS idx_vehicle_details_make_model
ON vehicle_details(make, model);

CREATE INDEX IF NOT EXISTS idx_vehicle_details_location
ON vehicle_details(location_id);

CREATE INDEX IF NOT EXISTS idx_vehicle_details_posted_date
ON vehicle_details(posted_date);
```

**Purpose:** Store all vehicle details for each listing

**Key Fields:**
- `listing_id` - Foreign key to seen_listings
- `make`, `model`, `year` - Car identification
- `price`, `currency` - Pricing info
- `mileage_km`, `fuel_type`, `transmission` - Key specs for notifications
- `location`, `seller_name` - Contact info
- `url` - Direct link to listing
- `posted_date` - When listing was posted (helps identify "new")

**Usage in Notifications:**
```python
# When sending WhatsApp notification
SELECT
    make, model, year, price, currency,
    mileage_km, fuel_type, transmission, location,
    seller_name, url, primary_image_url
FROM vehicle_details
WHERE listing_id = '119084515'
```

---

### Table 3: search_configurations

```sql
CREATE TABLE IF NOT EXISTS search_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    search_url TEXT,
    vehicle_make TEXT,
    vehicle_model TEXT,
    year_from INTEGER,
    year_to INTEGER,
    price_from REAL,
    price_to REAL,
    currency_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMP
);
```

**Purpose:** Store your multiple search URLs for monitoring

**Example Data:**
```json
{
    "id": 1,
    "name": "Toyota Land Cruiser Prado (1995-2008, $11K-$18K)",
    "search_url": "https://www.myauto.ge/ka/s/...",
    "vehicle_make": "Toyota",
    "vehicle_model": "Land Cruiser",
    "year_from": 1995,
    "year_to": 2008,
    "price_from": 11000,
    "price_to": 18000,
    "currency_id": 1,  // USD
    "is_active": 1,
    "created_at": "2024-11-09T10:30:00Z",
    "last_checked_at": "2024-11-09T11:45:00Z"
}
```

**Usage:**
```sql
-- Get all active searches
SELECT * FROM search_configurations WHERE is_active = 1;

-- Update last checked time
UPDATE search_configurations
SET last_checked_at = datetime('now')
WHERE id = 1;
```

---

### Table 4: notifications_sent

```sql
CREATE TABLE IF NOT EXISTS notifications_sent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id TEXT REFERENCES seen_listings(id),
    notification_type TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    whatsapp_message_id TEXT,
    success BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_notifications_sent_listing_id
ON notifications_sent(listing_id);

CREATE INDEX IF NOT EXISTS idx_notifications_sent_sent_at
ON notifications_sent(sent_at);
```

**Purpose:** Track all notifications sent (for debugging and history)

**notification_type Values:**
- `new_listing` - New car found
- `no_listings` - Heartbeat message (status update)
- `error` - Error notification

**Usage:**
```sql
-- Check how many notifications sent in last 24 hours
SELECT COUNT(*) FROM notifications_sent
WHERE sent_at > datetime('now', '-1 day');

-- Find failed notifications
SELECT * FROM notifications_sent WHERE success = 0;
```

---

## Database Initialization Script

Create file: `db_init.py`

```python
#!/usr/bin/env python3
"""
Database initialization script
Creates all tables with proper schema
"""

from libsql_client import create_client
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize Turso database with schema"""

    # Get connection
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")

    if not url or not token:
        logger.error("❌ Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN")
        return False

    try:
        client = create_client(database_url=url, auth_token=token)
        logger.info("✅ Connected to Turso database")

        # Create tables
        sql_script = """
        -- Table 1: seen_listings
        CREATE TABLE IF NOT EXISTS seen_listings (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_notified_at TIMESTAMP,
            notified BOOLEAN DEFAULT 1
        );

        CREATE INDEX IF NOT EXISTS idx_seen_listings_created_at
        ON seen_listings(created_at);

        -- Table 2: vehicle_details
        CREATE TABLE IF NOT EXISTS vehicle_details (
            listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,
            make TEXT,
            make_id INTEGER,
            model TEXT,
            model_id INTEGER,
            modification TEXT,
            year INTEGER,
            vin TEXT UNIQUE,
            body_type TEXT,
            color TEXT,
            interior_color TEXT,
            doors INTEGER,
            seats INTEGER,
            wheel_position TEXT,
            drive_type TEXT,
            fuel_type TEXT,
            fuel_type_id INTEGER,
            displacement_liters REAL,
            transmission TEXT,
            power_hp INTEGER,
            cylinders INTEGER,
            status TEXT,
            mileage_km INTEGER,
            mileage_unit TEXT,
            customs_cleared BOOLEAN,
            technical_inspection_passed BOOLEAN,
            condition_description TEXT,
            price REAL,
            currency TEXT,
            currency_id INTEGER,
            negotiable BOOLEAN,
            installment_available BOOLEAN,
            exchange_possible BOOLEAN,
            seller_type TEXT,
            seller_name TEXT,
            seller_phone TEXT,
            location TEXT,
            location_id INTEGER,
            is_dealer BOOLEAN,
            dealer_id INTEGER,
            primary_image_url TEXT,
            photo_count INTEGER,
            video_url TEXT,
            posted_date TIMESTAMP,
            last_updated TIMESTAMP,
            url TEXT,
            view_count INTEGER,
            is_vip BOOLEAN,
            is_featured BOOLEAN
        );

        CREATE INDEX IF NOT EXISTS idx_vehicle_details_year
        ON vehicle_details(year);

        CREATE INDEX IF NOT EXISTS idx_vehicle_details_price
        ON vehicle_details(price);

        CREATE INDEX IF NOT EXISTS idx_vehicle_details_make_model
        ON vehicle_details(make, model);

        CREATE INDEX IF NOT EXISTS idx_vehicle_details_location
        ON vehicle_details(location_id);

        CREATE INDEX IF NOT EXISTS idx_vehicle_details_posted_date
        ON vehicle_details(posted_date);

        -- Table 3: search_configurations
        CREATE TABLE IF NOT EXISTS search_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            search_url TEXT,
            vehicle_make TEXT,
            vehicle_model TEXT,
            year_from INTEGER,
            year_to INTEGER,
            price_from REAL,
            price_to REAL,
            currency_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_checked_at TIMESTAMP
        );

        -- Table 4: notifications_sent
        CREATE TABLE IF NOT EXISTS notifications_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id TEXT REFERENCES seen_listings(id),
            notification_type TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            whatsapp_message_id TEXT,
            success BOOLEAN
        );

        CREATE INDEX IF NOT EXISTS idx_notifications_sent_listing_id
        ON notifications_sent(listing_id);

        CREATE INDEX IF NOT EXISTS idx_notifications_sent_sent_at
        ON notifications_sent(sent_at);
        """

        # Execute schema
        client.execute(sql_script)
        logger.info("✅ Database schema created successfully")

        # Verify tables exist
        result = client.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )

        tables = [row[0] for row in result]
        logger.info(f"✅ Tables created: {', '.join(tables)}")

        if len(tables) >= 4:
            logger.info("✅ ALL TABLES CREATED SUCCESSFULLY")
            return True
        else:
            logger.error("❌ Some tables failed to create")
            return False

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
```

---

## Database Operations Helper

Create file: `db_operations.py`

```python
#!/usr/bin/env python3
"""
Database operations helper
Common database queries
"""

from libsql_client import create_client
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.url = os.getenv("TURSO_DATABASE_URL")
        self.token = os.getenv("TURSO_AUTH_TOKEN")
        self.client = None

    def connect(self):
        """Connect to database"""
        if not self.url or not self.token:
            logger.error("Missing database credentials")
            return False

        try:
            self.client = create_client(database_url=self.url, auth_token=self.token)
            logger.info("✅ Connected to database")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def has_seen_listing(self, listing_id):
        """Check if listing ID was already processed"""
        try:
            result = self.client.execute(
                "SELECT 1 FROM seen_listings WHERE id = ?",
                [listing_id]
            )
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking listing: {e}")
            return False

    def save_listing(self, listing_data):
        """Save new listing to database"""
        try:
            listing_id = listing_data.get('listing_id')
            now = datetime.now().isoformat()

            # Insert into seen_listings
            self.client.execute(
                """INSERT INTO seen_listings (id, created_at, notified)
                   VALUES (?, ?, ?)""",
                [listing_id, now, 1]
            )

            # Insert into vehicle_details
            self.client.execute(
                """INSERT INTO vehicle_details
                   (listing_id, make, model, year, price, currency,
                    mileage_km, fuel_type, transmission, location,
                    seller_name, url, posted_date, primary_image_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    listing_id,
                    listing_data.get('vehicle', {}).get('make'),
                    listing_data.get('vehicle', {}).get('model'),
                    listing_data.get('vehicle', {}).get('year'),
                    listing_data.get('pricing', {}).get('price'),
                    listing_data.get('pricing', {}).get('currency'),
                    listing_data.get('condition', {}).get('mileage_km'),
                    listing_data.get('engine', {}).get('fuel_type'),
                    listing_data.get('engine', {}).get('transmission'),
                    listing_data.get('seller', {}).get('location'),
                    listing_data.get('seller', {}).get('seller_name'),
                    listing_data.get('url'),
                    listing_data.get('posted_date'),
                    listing_data.get('media', {}).get('photos', [None])[0]
                ]
            )

            logger.info(f"✅ Saved listing: {listing_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving listing: {e}")
            return False

    def cleanup_old_listings(self, days=365):
        """Delete listings older than specified days"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            self.client.execute(
                "DELETE FROM seen_listings WHERE created_at < ?",
                [cutoff]
            )
            logger.info(f"✅ Cleaned up listings older than {days} days")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")
            return False

    def get_search_configs(self):
        """Get all active search configurations"""
        try:
            result = self.client.execute(
                "SELECT * FROM search_configurations WHERE is_active = 1"
            )
            return result
        except Exception as e:
            logger.error(f"Error getting configs: {e}")
            return []

    def update_last_checked(self, search_id):
        """Update last checked time for search"""
        try:
            self.client.execute(
                "UPDATE search_configurations SET last_checked_at = ? WHERE id = ?",
                [datetime.now().isoformat(), search_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error updating: {e}")
            return False

    def log_notification(self, listing_id, notification_type, success, message_id=None):
        """Log a sent notification"""
        try:
            self.client.execute(
                """INSERT INTO notifications_sent
                   (listing_id, notification_type, success, whatsapp_message_id)
                   VALUES (?, ?, ?, ?)""",
                [listing_id, notification_type, 1 if success else 0, message_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            return False
```

---

## Data Field Reference

### MyAuto.ge Listing Fields (Based on Research)

| Field Name | Data Type | Example | Required | Notes |
|-----------|-----------|---------|----------|-------|
| listing_id | TEXT | "119084515" | YES | Unique identifier |
| make | TEXT | "Toyota" | YES | Car manufacturer |
| model | TEXT | "Land Cruiser" | YES | Car model |
| year | INTEGER | 2001 | YES | Manufacturing year |
| price | REAL | 15500 | YES | Price amount |
| currency | TEXT | "USD" | YES | Currency code |
| mileage_km | INTEGER | 250000 | YES | Mileage reading |
| fuel_type | TEXT | "Diesel" | YES | Fuel type |
| transmission | TEXT | "Automatic" | NO | Manual/Automatic |
| location | TEXT | "Tbilisi" | NO | Location name |
| url | TEXT | URL string | YES | Listing URL |
| posted_date | TIMESTAMP | ISO 8601 | NO | When listed |
| seller_name | TEXT | "John Doe" | NO | Seller name |
| customs_cleared | BOOLEAN | 1 | NO | Import status |

---

## Backup & Recovery

### Backup Your Data

```python
# Export all listings
import json
from datetime import datetime

def backup_database():
    """Backup all vehicle details to JSON"""
    result = client.execute(
        "SELECT * FROM vehicle_details ORDER BY posted_date DESC"
    )

    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(result, f, indent=2)

    return backup_file
```

---

## Performance Optimization

### Index Strategy

All critical indexes are created:
- `year` - Fast filtering by year
- `price` - Fast filtering by price
- `make_model` - Fast search by brand
- `location` - Fast location-based queries
- `posted_date` - Fast sorting by date

### Query Performance Tips

```sql
-- FAST: Uses index
SELECT * FROM vehicle_details WHERE year = 2001;

-- FAST: Uses compound index
SELECT * FROM vehicle_details WHERE make = 'Toyota' AND model = 'Land Cruiser';

-- SLOW: No index (avoid)
SELECT * FROM vehicle_details WHERE color = 'Black';
```

---

**Database ready for implementation!** 🚀

