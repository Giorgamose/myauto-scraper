-- ============================================================================
-- Multi-User System Migration
-- Supabase SQL Schema Update
-- ============================================================================
--
-- This migration converts the system from chat_id-based identification to
-- proper user account management with individual search criteria and
-- subscription management.
--
-- CHANGES:
-- 1. Create users table (explicit user management)
-- 2. Create user_api_tokens table (API access for users)
-- 3. Create user_search_criteria table (dynamic search configurations)
-- 4. Update existing tables to reference user_id
-- 5. Create views for multi-user analytics
--
-- ============================================================================

-- ============================================================================
-- Table 1: Telegram Users
-- Central user management table (Telegram-native)
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Telegram identification (PRIMARY IDENTIFIER)
    telegram_chat_id BIGINT UNIQUE NOT NULL,
    telegram_user_id BIGINT,
    telegram_username TEXT,

    -- User profile info
    first_name TEXT,
    last_name TEXT,

    -- Account status
    is_active BOOLEAN DEFAULT TRUE,

    -- Preferences
    notification_enabled BOOLEAN DEFAULT TRUE,
    check_interval_minutes INTEGER DEFAULT 15,
    max_subscriptions INTEGER DEFAULT 50,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT max_subscriptions_positive CHECK (max_subscriptions > 0),
    CONSTRAINT check_interval_positive CHECK (check_interval_minutes > 0)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_users_chat_id ON telegram_users(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_user_id ON telegram_users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_is_active ON telegram_users(is_active);
CREATE INDEX IF NOT EXISTS idx_telegram_users_last_seen ON telegram_users(last_seen);

-- ============================================================================
-- Table 2: User API Tokens
-- For programmatic access (optional, not required for Telegram bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_user_api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to Telegram user
    telegram_user_id UUID NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,

    -- Token information
    token_hash TEXT NOT NULL UNIQUE,
    token_name TEXT NOT NULL,

    -- Access control
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_user_api_tokens_user_id ON telegram_user_api_tokens(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_user_api_tokens_token_hash ON telegram_user_api_tokens(token_hash);

-- ============================================================================
-- Table 3: Telegram User Search Criteria (replaces hardcoded config.json)
-- Each Telegram user can define their own search filter sets
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_user_search_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to Telegram user
    telegram_user_id UUID NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,

    -- Criteria metadata
    criteria_name TEXT NOT NULL,
    description TEXT,

    -- Search parameters (stored as JSON for flexibility)
    search_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Example structure of search_parameters:
    -- {
    --   "vehicleType": 0,
    --   "makes": [1, 2, 3],
    --   "models": [10, 11, 12],
    --   "priceFrom": 5000,
    --   "priceTo": 50000,
    --   "yearFrom": 2000,
    --   "yearTo": 2024,
    --   "fuelTypes": [1, 2, 3],
    --   "transmission": [1, 2],
    --   "mileageFrom": 0,
    --   "mileageTo": 500000,
    --   "customs": 1,
    --   "locations": [1, 2, 3],
    --   "engineVolumeFrom": 0,
    --   "engineVolumeTo": 8000,
    --   "seatCount": null,
    --   "doorsCount": null,
    --   "colorId": null
    -- }

    -- Notification settings
    notification_enabled BOOLEAN DEFAULT TRUE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(telegram_user_id, criteria_name),
    CONSTRAINT criteria_name_length CHECK (length(criteria_name) >= 3 AND length(criteria_name) <= 100)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_user_search_criteria_user_id ON telegram_user_search_criteria(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_user_search_criteria_is_active ON telegram_user_search_criteria(is_active);
CREATE INDEX IF NOT EXISTS idx_telegram_user_search_criteria_created_at ON telegram_user_search_criteria(created_at);

-- ============================================================================
-- Table 4: Updated Telegram User Subscriptions
-- Links to both Telegram users and search criteria
-- ============================================================================
-- MIGRATION STRATEGY: Rename old table, create new one, copy data

-- First, rename old table
ALTER TABLE IF EXISTS user_subscriptions RENAME TO user_subscriptions_old;

-- Create new telegram_user_subscriptions table with telegram_user_id reference
CREATE TABLE IF NOT EXISTS telegram_user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to Telegram user (primary identifier)
    telegram_user_id UUID NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,

    -- MyAuto.ge search URL
    search_url TEXT NOT NULL,

    -- Optional friendly name for the search
    search_name TEXT,

    -- Optional reference to telegram_user_search_criteria (if created from criteria)
    search_criteria_id UUID REFERENCES telegram_user_search_criteria(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE,

    -- Soft delete flag
    is_active BOOLEAN DEFAULT TRUE,

    -- Ensure each user doesn't have duplicate URLs
    UNIQUE(telegram_user_id, search_url),

    -- Keep old chat_id for legacy reference during migration
    chat_id BIGINT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_user_subscriptions_user_id ON telegram_user_subscriptions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_user_subscriptions_is_active ON telegram_user_subscriptions(is_active);
CREATE INDEX IF NOT EXISTS idx_telegram_user_subscriptions_last_checked ON telegram_user_subscriptions(last_checked);

-- ============================================================================
-- Table 5: Updated Telegram User Seen Listings
-- Links to Telegram users (deduplication per user)
-- ============================================================================
-- MIGRATION STRATEGY: Similar to subscriptions

-- Rename old table
ALTER TABLE IF EXISTS user_seen_listings RENAME TO user_seen_listings_old;

-- Create new table
CREATE TABLE IF NOT EXISTS telegram_user_seen_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to Telegram user
    telegram_user_id UUID NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,

    -- MyAuto listing ID
    listing_id TEXT NOT NULL,

    -- When user first saw this listing
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure no duplicate entries per user/listing
    UNIQUE(telegram_user_id, listing_id),

    -- Keep old chat_id for legacy reference
    chat_id BIGINT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_user_seen_listings_user_id ON telegram_user_seen_listings(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_user_seen_listings_listing_id ON telegram_user_seen_listings(listing_id);
CREATE INDEX IF NOT EXISTS idx_telegram_user_seen_listings_seen_at ON telegram_user_seen_listings(seen_at);

-- ============================================================================
-- Table 6: Updated Telegram Bot Events
-- Links to Telegram users (logging and monitoring)
-- ============================================================================
-- Rename old table
ALTER TABLE IF EXISTS bot_events RENAME TO bot_events_old;

-- Create new table
CREATE TABLE IF NOT EXISTS telegram_bot_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to Telegram user
    telegram_user_id UUID NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,

    -- Type of event (subscription_added, command_executed, error, etc.)
    event_type TEXT NOT NULL,

    -- Additional event data (flexible JSON)
    event_data JSONB,

    -- When event occurred
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Keep old chat_id for legacy reference
    chat_id BIGINT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telegram_bot_events_user_id ON telegram_bot_events(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_bot_events_event_type ON telegram_bot_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telegram_bot_events_created_at ON telegram_bot_events(created_at DESC);

-- ============================================================================
-- Data Migration: Copy data from old tables to new tables
-- NOTE: This migrates existing chat_id data to new user_id structure
-- ============================================================================

-- Step 1: Create Telegram users from existing chat_ids
-- You'll need to run this manually after running the schema creation
-- INSERT INTO telegram_users (telegram_chat_id, telegram_user_id, first_name, last_name)
-- SELECT DISTINCT
--     chat_id,
--     NULL,  -- telegram_user_id, fill manually if available
--     'User',  -- default first name
--     chat_id::TEXT  -- use chat_id as last name for uniqueness
-- FROM (
--     SELECT DISTINCT chat_id FROM user_subscriptions_old
--     UNION
--     SELECT DISTINCT chat_id FROM user_seen_listings_old
--     UNION
--     SELECT DISTINCT chat_id FROM bot_events_old
-- ) as distinct_chats
-- WHERE chat_id IS NOT NULL;

-- Step 2: Copy subscriptions (commented out - run after users created)
-- INSERT INTO telegram_user_subscriptions (telegram_user_id, search_url, search_name, created_at, last_checked, is_active, chat_id)
-- SELECT
--     tu.id,
--     old.search_url,
--     old.search_name,
--     old.created_at,
--     old.last_checked,
--     old.is_active,
--     old.chat_id
-- FROM user_subscriptions_old old
-- JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
-- WHERE old.chat_id IS NOT NULL;

-- Step 3: Copy seen listings
-- INSERT INTO telegram_user_seen_listings (telegram_user_id, listing_id, seen_at, chat_id)
-- SELECT
--     tu.id,
--     old.listing_id,
--     old.seen_at,
--     old.chat_id
-- FROM user_seen_listings_old old
-- JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
-- WHERE old.chat_id IS NOT NULL;

-- Step 4: Copy bot events
-- INSERT INTO telegram_bot_events (telegram_user_id, event_type, event_data, created_at, chat_id)
-- SELECT
--     tu.id,
--     old.event_type,
--     old.event_data,
--     old.created_at,
--     old.chat_id
-- FROM bot_events_old old
-- JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
-- WHERE old.chat_id IS NOT NULL;

-- ============================================================================
-- UPDATED VIEWS for Telegram Multi-User Analytics
-- ============================================================================

-- View: Active subscriptions per Telegram user
CREATE OR REPLACE VIEW telegram_user_subscriptions_active AS
SELECT
    tu.id as telegram_user_id,
    tu.telegram_chat_id,
    tu.first_name,
    tu.last_name,
    COUNT(tus.id) as subscription_count,
    MAX(tus.created_at) as most_recent,
    MAX(tus.last_checked) as last_check
FROM telegram_users tu
LEFT JOIN telegram_user_subscriptions tus ON tu.id = tus.telegram_user_id AND tus.is_active = TRUE
WHERE tu.is_active = TRUE
GROUP BY tu.id, tu.telegram_chat_id, tu.first_name, tu.last_name;

-- View: Telegram user search criteria statistics
CREATE OR REPLACE VIEW telegram_user_search_criteria_stats AS
SELECT
    tu.id as telegram_user_id,
    tu.telegram_chat_id,
    COUNT(tusc.id) as criteria_count,
    COUNT(CASE WHEN tusc.is_active = TRUE THEN 1 END) as active_criteria,
    MAX(tusc.created_at) as most_recent_criteria
FROM telegram_users tu
LEFT JOIN telegram_user_search_criteria tusc ON tu.id = tusc.telegram_user_id
WHERE tu.is_active = TRUE
GROUP BY tu.id, tu.telegram_chat_id;

-- View: Telegram subscription statistics
CREATE OR REPLACE VIEW telegram_subscription_stats AS
SELECT
    COUNT(DISTINCT tu.id) as total_active_users,
    COUNT(DISTINCT tus.id) as total_active_subscriptions,
    COUNT(DISTINCT CASE WHEN tus.last_checked IS NOT NULL THEN tu.id END) as checked_users,
    MAX(tus.last_checked) as most_recent_check,
    ROUND(
        CAST(COUNT(DISTINCT tus.id) AS DECIMAL) /
        NULLIF(COUNT(DISTINCT tu.id), 0),
        2
    ) as avg_subscriptions_per_user
FROM telegram_users tu
LEFT JOIN telegram_user_subscriptions tus ON tu.id = tus.telegram_user_id AND tus.is_active = TRUE
WHERE tu.is_active = TRUE;

-- View: Telegram bot event summary (last 7 days)
CREATE OR REPLACE VIEW telegram_bot_events_recent AS
SELECT
    tu.id as telegram_user_id,
    tu.telegram_chat_id,
    tbe.event_type,
    COUNT(*) as event_count,
    MAX(tbe.created_at) as last_event
FROM telegram_users tu
LEFT JOIN telegram_bot_events tbe ON tu.id = tbe.telegram_user_id AND tbe.created_at > NOW() - INTERVAL '7 days'
WHERE tu.is_active = TRUE
GROUP BY tu.id, tu.telegram_chat_id, tbe.event_type
ORDER BY tu.id, last_event DESC;

-- ============================================================================
-- UPDATED CLEANUP FUNCTIONS (Telegram-specific)
-- ============================================================================

-- Function: Remove old seen listings (older than 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_telegram_seen_listings()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    DELETE FROM telegram_user_seen_listings
    WHERE seen_at < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- Function: Mark subscriptions as inactive if not checked in 90 days
CREATE OR REPLACE FUNCTION cleanup_inactive_telegram_subscriptions()
RETURNS TABLE(updated_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    UPDATE telegram_user_subscriptions
    SET is_active = FALSE
    WHERE is_active = TRUE
    AND last_checked IS NOT NULL
    AND last_checked < NOW() - INTERVAL '90 days';

    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- Function: Deactivate inactive Telegram users (no activity for 180 days)
CREATE OR REPLACE FUNCTION deactivate_inactive_telegram_users()
RETURNS TABLE(updated_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    UPDATE telegram_users
    SET is_active = FALSE
    WHERE is_active = TRUE
    AND last_seen IS NOT NULL
    AND last_seen < NOW() - INTERVAL '180 days';

    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these to verify migration was successful
-- ============================================================================

-- Check if new Telegram tables exist and have correct structure
SELECT
    table_name,
    CASE
        WHEN table_name = 'telegram_users' THEN 'Telegram user management'
        WHEN table_name = 'telegram_user_api_tokens' THEN 'API token storage'
        WHEN table_name = 'telegram_user_search_criteria' THEN 'Dynamic search criteria'
        WHEN table_name = 'telegram_user_subscriptions' THEN 'User subscriptions (updated)'
        WHEN table_name = 'telegram_user_seen_listings' THEN 'Seen listings (updated)'
        WHEN table_name = 'telegram_bot_events' THEN 'Bot events (updated)'
    END as description
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'telegram_users',
    'telegram_user_api_tokens',
    'telegram_user_search_criteria',
    'telegram_user_subscriptions',
    'telegram_user_seen_listings',
    'telegram_bot_events'
)
ORDER BY table_name;

-- ============================================================================
-- MIGRATION CHECKLIST - TELEGRAM MULTI-USER SYSTEM
-- ============================================================================
--
-- [ ] 1. Run this entire script in Supabase SQL Editor
--        Expected: All tables, views, and functions created successfully
--
-- [ ] 2. Verify Telegram tables were created:
--        SELECT * FROM information_schema.tables
--        WHERE table_schema = 'public' AND table_name LIKE 'telegram%';
--
-- [ ] 3. Create Telegram users from existing chat_ids (if migrating):
--        - Uncomment Step 1 from Data Migration section above
--        - Run the INSERT INTO telegram_users statement
--        - Verify users were created: SELECT COUNT(*) FROM telegram_users;
--
-- [ ] 4. Migrate data from old tables to new tables:
--        - Uncomment Step 2 (subscriptions) and run
--        - Uncomment Step 3 (seen listings) and run
--        - Uncomment Step 4 (bot events) and run
--        - Verify data: SELECT COUNT(*) FROM telegram_user_subscriptions;
--
-- [ ] 5. Update Python code to use new table names:
--        telegram_users instead of users table
--        telegram_user_subscriptions instead of user_subscriptions
--        telegram_user_seen_listings instead of user_seen_listings
--        telegram_bot_events instead of bot_events
--
-- [ ] 6. Test all operations with new schema:
--        - Add subscription for a Telegram user
--        - Record seen listings
--        - Log events
--        - Verify deduplication works
--
-- [ ] 7. Verify views work:
--        SELECT * FROM telegram_user_subscriptions_active;
--        SELECT * FROM telegram_subscription_stats;
--        SELECT * FROM telegram_bot_events_recent;
--
-- [ ] 8. (Optional) Drop old tables after verification:
--        DROP TABLE user_subscriptions_old;
--        DROP TABLE user_seen_listings_old;
--        DROP TABLE bot_events_old;
--
-- ============================================================================
