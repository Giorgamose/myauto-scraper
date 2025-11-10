-- ============================================================================
-- Table: user_seen_listings
-- Prevents duplicate notifications by tracking which listings users have seen
-- ============================================================================
-- Run this SQL in Supabase SQL Editor to create the table
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_seen_listings (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID
    chat_id BIGINT NOT NULL,

    -- MyAuto listing ID (to track which cars user has already seen)
    listing_id TEXT NOT NULL,

    -- When user first saw this listing
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure no duplicate entries per user/listing
    UNIQUE(chat_id, listing_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_seen_listings_chat_id
    ON user_seen_listings(chat_id);

CREATE INDEX IF NOT EXISTS idx_user_seen_listings_listing_id
    ON user_seen_listings(listing_id);

CREATE INDEX IF NOT EXISTS idx_user_seen_listings_seen_at
    ON user_seen_listings(seen_at);

-- Verify table was created
SELECT * FROM user_seen_listings LIMIT 0;

-- ============================================================================
-- Expected output:
-- "SUCCESS: Table created"
--
-- If you see an error about "already exists", that's fine - it means
-- the table was already created.
--
-- This table is used internally by the bot to prevent sending
-- duplicate notifications about the same car listing to the same user.
-- ============================================================================
