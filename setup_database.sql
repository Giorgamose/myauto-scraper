-- MyAuto Car Listing Monitor - Database Schema Setup
--
-- HOW TO USE THIS SCRIPT:
-- 1. Go to: https://app.supabase.com
-- 2. Select your project (efohkibukutjvrrhhxdn)
-- 3. Click "SQL Editor" in the left sidebar
-- 4. Click "+ New Query"
-- 5. Copy all the SQL below and paste it
-- 6. Click "Run"
--
-- This will create all required tables for the monitoring system
--

-- Table 1: seen_listings - Track which listings have been seen
CREATE TABLE IF NOT EXISTS seen_listings (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_notified_at TEXT,
    notified INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_listings_created_at ON seen_listings(created_at);

-- Table 2: vehicle_details - Complete vehicle information for each listing
CREATE TABLE IF NOT EXISTS vehicle_details (
    listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,
    make TEXT,
    make_id INTEGER,
    model TEXT,
    model_id INTEGER,
    modification TEXT,
    year INTEGER,
    vin TEXT,
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
    customs_cleared INTEGER,
    technical_inspection_passed INTEGER,
    condition_description TEXT,
    price REAL,
    currency TEXT,
    currency_id INTEGER,
    negotiable INTEGER,
    installment_available INTEGER,
    exchange_possible INTEGER,
    seller_type TEXT,
    seller_name TEXT,
    seller_phone TEXT,
    location TEXT,
    location_id INTEGER,
    is_dealer INTEGER,
    dealer_id INTEGER,
    primary_image_url TEXT,
    photo_count INTEGER,
    video_url TEXT,
    posted_date TEXT,
    last_updated TEXT,
    url TEXT,
    view_count INTEGER,
    is_vip INTEGER,
    is_featured INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vehicle_make ON vehicle_details(make);

-- Table 3: search_configurations - Store search configurations
CREATE TABLE IF NOT EXISTS search_configurations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    search_url TEXT,
    vehicle_make TEXT,
    vehicle_model TEXT,
    year_from INTEGER,
    year_to INTEGER,
    price_from REAL,
    price_to REAL,
    currency_id INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    last_checked_at TIMESTAMP
);

-- Table 4: notifications_sent - Track sent notifications
CREATE TABLE IF NOT EXISTS notifications_sent (
    id SERIAL PRIMARY KEY,
    listing_id TEXT REFERENCES seen_listings(id) ON DELETE CASCADE,
    notification_type TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    telegram_message_id TEXT,
    success INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_sent(sent_at);

-- After running this script, verify the tables exist by running:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
