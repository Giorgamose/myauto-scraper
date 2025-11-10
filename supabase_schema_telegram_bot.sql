-- ============================================================================
-- Telegram Bot Tables - Supabase SQL Schema
-- ============================================================================
--
-- Run these SQL commands in your Supabase SQL Editor to create tables
-- for the Telegram bot user subscriptions feature.
--
-- Location: Supabase Dashboard → SQL Editor → New query
-- Copy all code below and execute
--
-- ============================================================================

-- Table 1: User Subscriptions
-- Stores the MyAuto search URLs that users want to monitor
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID (users/groups)
    chat_id BIGINT NOT NULL,

    -- MyAuto.ge search URL
    search_url TEXT NOT NULL,

    -- Optional friendly name for the search
    search_name TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE,

    -- Soft delete flag (false = deleted/inactive)
    is_active BOOLEAN DEFAULT TRUE,

    -- Ensure each user doesn't have duplicate URLs
    UNIQUE(chat_id, search_url)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_chat_id
    ON user_subscriptions(chat_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_is_active
    ON user_subscriptions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_last_checked
    ON user_subscriptions(last_checked);

-- ============================================================================
-- Table 2: User Seen Listings
-- Prevents duplicate notifications by tracking which listings users have seen
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_seen_listings (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID
    chat_id BIGINT NOT NULL,

    -- MyAuto listing ID
    listing_id TEXT NOT NULL,

    -- When user first saw this listing
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure no duplicate entries per user/listing
    UNIQUE(chat_id, listing_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_seen_listings_chat_id
    ON user_seen_listings(chat_id);
CREATE INDEX IF NOT EXISTS idx_user_seen_listings_listing_id
    ON user_seen_listings(listing_id);
CREATE INDEX IF NOT EXISTS idx_user_seen_listings_seen_at
    ON user_seen_listings(seen_at);

-- ============================================================================
-- Table 3: Bot Events
-- Logs bot interactions for debugging and monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS bot_events (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID
    chat_id BIGINT NOT NULL,

    -- Type of event (e.g., "subscription_added", "command_executed")
    event_type TEXT NOT NULL,

    -- Additional event data as JSON
    event_data JSONB,

    -- When event occurred
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bot_events_chat_id
    ON bot_events(chat_id);
CREATE INDEX IF NOT EXISTS idx_bot_events_event_type
    ON bot_events(event_type);
CREATE INDEX IF NOT EXISTS idx_bot_events_created_at
    ON bot_events(created_at DESC);

-- ============================================================================
-- Optional: Enable Row Level Security (RLS) for security
-- ============================================================================
-- Uncomment below if you want to restrict access by chat_id
-- This adds an extra layer of security (optional)

-- ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_seen_listings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bot_events ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- Views (Optional)
-- ============================================================================

-- View: Active subscriptions per user
CREATE OR REPLACE VIEW user_subscriptions_active AS
SELECT
    chat_id,
    COUNT(*) as subscription_count,
    MAX(created_at) as most_recent,
    MAX(last_checked) as last_check
FROM user_subscriptions
WHERE is_active = TRUE
GROUP BY chat_id;

-- View: Subscription statistics
CREATE OR REPLACE VIEW subscription_stats AS
SELECT
    COUNT(DISTINCT chat_id) as total_active_users,
    COUNT(*) as total_active_subscriptions,
    COUNT(DISTINCT CASE WHEN last_checked IS NOT NULL THEN chat_id END) as checked_users,
    MAX(last_checked) as most_recent_check
FROM user_subscriptions
WHERE is_active = TRUE;

-- View: Bot event summary (last 7 days)
CREATE OR REPLACE VIEW bot_events_recent AS
SELECT
    chat_id,
    event_type,
    COUNT(*) as event_count,
    MAX(created_at) as last_event
FROM bot_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY chat_id, event_type
ORDER BY chat_id, last_event DESC;

-- ============================================================================
-- Cleanup Function (Optional)
-- Automatically remove old seen listings
-- ============================================================================
CREATE OR REPLACE FUNCTION cleanup_old_seen_listings()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    -- Delete seen listings older than 30 days
    DELETE FROM user_seen_listings
    WHERE seen_at < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Cleanup Function (Optional)
-- Mark subscriptions as inactive if not checked in 90 days
-- ============================================================================
CREATE OR REPLACE FUNCTION cleanup_inactive_subscriptions()
RETURNS TABLE(updated_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    -- Mark as inactive if not checked in 90 days
    UPDATE user_subscriptions
    SET is_active = FALSE
    WHERE is_active = TRUE
    AND last_checked IS NOT NULL
    AND last_checked < NOW() - INTERVAL '90 days';

    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Notes
-- ============================================================================
--
-- 1. After running this script, tables will be created in your Supabase database
--
-- 2. The bot will use the existing database_rest_api.py to access these tables
--
-- 3. Soft Delete: Subscriptions are marked inactive (is_active=false) rather
--    than deleted. This preserves referential integrity and allows recovery.
--
-- 4. Indexes: Created for frequently queried columns to improve performance
--
-- 5. Views: Optional views for analytics and monitoring
--
-- 6. Cleanup Functions: Optional functions that can be run via cron jobs
--    to maintain table sizes. Example cron usage:
--    SELECT cron.schedule('cleanup-seen-listings', '0 0 * * *', 'SELECT cleanup_old_seen_listings()');
--    SELECT cron.schedule('cleanup-inactive-subs', '0 1 * * *', 'SELECT cleanup_inactive_subscriptions()');
--
-- 7. This schema is designed to coexist with your existing tables
--    (seen_listings, vehicle_details, search_configurations, notifications_sent)
--
-- ============================================================================

-- Verify tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user_subscriptions', 'user_seen_listings', 'bot_events')
ORDER BY table_name;

-- You should see:
-- user_seen_listings
-- user_subscriptions
-- bot_events
