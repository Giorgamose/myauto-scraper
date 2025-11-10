-- MyAuto Car Listing Monitor - Database Schema (All VARCHAR fields)
-- This schema uses VARCHAR for all fields to avoid type conversion issues
-- and handle Georgian text, mixed content, and flexible data types

-- HOW TO USE THIS SCRIPT:
-- 1. Go to: https://app.supabase.com
-- 2. Select your project (efohkibukutjvrrhhxdn)
-- 3. Click "SQL Editor" in the left sidebar
-- 4. Click "+ New Query"
-- 5. Copy all the SQL below and paste it
-- 6. Click "Run"

-- Drop old tables if they exist (BACKUP FIRST!)
-- DROP TABLE IF EXISTS notifications_sent CASCADE;
-- DROP TABLE IF EXISTS vehicle_details CASCADE;
-- DROP TABLE IF EXISTS search_configurations CASCADE;
-- DROP TABLE IF EXISTS seen_listings CASCADE;

-- Table 1: seen_listings - Track which listings have been seen
CREATE TABLE IF NOT EXISTS seen_listings (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_notified_at TEXT,
    notified TEXT DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_listings_created_at ON seen_listings(created_at);

-- Table 2: vehicle_details - Complete vehicle information for each listing
-- ALL fields are VARCHAR to handle Georgian text, mixed content, and flexible data
CREATE TABLE IF NOT EXISTS vehicle_details (
    listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,
    -- Vehicle identification
    make TEXT,
    model TEXT,
    year TEXT,
    category TEXT,  -- e.g., "ჯიპი" (Jeep), "სედანი" (Sedan), etc.
    vin TEXT,
    modification TEXT,

    -- Engine/Mechanical
    fuel_type TEXT,  -- e.g., "დიზელი" (Diesel), "ბენზინი" (Petrol)
    displacement_liters TEXT,  -- e.g., "4.2"
    cylinders TEXT,  -- e.g., "6"
    transmission TEXT,  -- e.g., "ტიპტრონიკი" (Tiptronic), "ხელით" (Manual)
    power_hp TEXT,  -- Horsepower
    drive_type TEXT,  -- e.g., "4x4", "ხელმძღვანელი" (Front-wheel)

    -- Body/Appearance
    body_type TEXT,
    color TEXT,  -- e.g., "შავი" (Black), "თეთრი" (White)
    interior_color TEXT,
    interior_material TEXT,  -- e.g., "ტყავი" (Leather)
    wheel_position TEXT,  -- "მარცხენა" (Left), "მარჯვენა" (Right)
    doors TEXT,  -- e.g., "4", "4/5"
    seats TEXT,  -- e.g., "5", "9"

    -- Condition
    status TEXT,
    mileage_km TEXT,  -- e.g., "446000", "446000 km"
    mileage_unit TEXT,  -- "km", "miles"
    customs_cleared TEXT,  -- "1", "0", "კი" (Yes), "არა" (No)
    technical_inspection_passed TEXT,  -- "1", "0", "კი", "არა"
    condition_description TEXT,  -- Full description of vehicle condition

    -- Pricing
    price TEXT,  -- e.g., "42000", "42,000", "42000 ₾"
    currency TEXT,  -- "USD", "GEL", "EUR"
    negotiable TEXT,  -- "1", "0", "კი", "არა"
    installment_available TEXT,  -- "1", "0", "კი", "არა"
    exchange_possible TEXT,  -- "1", "0", "კი", "არა"

    -- Special attributes
    has_catalytic_converter TEXT,  -- "1", "0", "კი", "არა"

    -- Seller information
    seller_type TEXT,  -- "Individual", "Dealer", etc.
    seller_name TEXT,
    seller_phone TEXT,
    location TEXT,  -- City/Region name
    is_dealer TEXT,  -- "1", "0"

    -- Media
    primary_image_url TEXT,
    photo_count TEXT,  -- Number of photos
    video_url TEXT,

    -- Metadata
    posted_date TEXT,
    last_updated TEXT,
    url TEXT,
    view_count TEXT,
    is_vip TEXT,  -- "1", "0"
    is_featured TEXT,  -- "1", "0"
    raw_data TEXT  -- Store raw JSON for debugging
);

CREATE INDEX IF NOT EXISTS idx_vehicle_make ON vehicle_details(make);
CREATE INDEX IF NOT EXISTS idx_vehicle_model ON vehicle_details(model);
CREATE INDEX IF NOT EXISTS idx_vehicle_year ON vehicle_details(year);
CREATE INDEX IF NOT EXISTS idx_vehicle_price ON vehicle_details(price);

-- Table 3: search_configurations - Store search configurations
CREATE TABLE IF NOT EXISTS search_configurations (
    id TEXT PRIMARY KEY,
    name TEXT,
    base_url TEXT,  -- Changed from search_url to match code
    parameters TEXT,  -- JSON-encoded query parameters
    vehicle_make TEXT,
    vehicle_model TEXT,
    year_from TEXT,
    year_to TEXT,
    price_from TEXT,
    price_to TEXT,
    is_active TEXT DEFAULT '1',  -- "1" or "0"
    created_at TEXT,
    last_checked_at TEXT
);

-- Table 4: notifications_sent - Track sent notifications
CREATE TABLE IF NOT EXISTS notifications_sent (
    id TEXT PRIMARY KEY,
    listing_id TEXT REFERENCES seen_listings(id) ON DELETE CASCADE,
    notification_type TEXT,  -- "telegram", "email", etc.
    sent_at TEXT,
    status TEXT  -- "sent", "failed", "pending"
);

CREATE INDEX IF NOT EXISTS idx_notifications_listing ON notifications_sent(listing_id);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_sent(sent_at);

-- Add comments explaining the schema
COMMENT ON TABLE vehicle_details IS 'All fields stored as TEXT (VARCHAR) for maximum flexibility with Georgian text and mixed data types';
COMMENT ON COLUMN vehicle_details.customs_cleared IS 'Accepts: 1/0, true/false, კი (yes)/არა (no)';
COMMENT ON COLUMN vehicle_details.technical_inspection_passed IS 'Accepts: 1/0, true/false, კი (yes)/არა (no)';
COMMENT ON COLUMN vehicle_details.price IS 'Accepts: numeric values with or without currency symbol or text';
