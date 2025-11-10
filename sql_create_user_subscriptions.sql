-- ============================================================================
-- Table: user_subscriptions
-- Stores the MyAuto search URLs that users want to monitor
-- ============================================================================
-- Run this SQL in Supabase SQL Editor to create the table
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID (users/groups)
    chat_id BIGINT NOT NULL,

    -- MyAuto.ge search URL to monitor
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_chat_id
    ON user_subscriptions(chat_id);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_is_active
    ON user_subscriptions(is_active);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_last_checked
    ON user_subscriptions(last_checked);

-- Verify table was created
SELECT * FROM user_subscriptions LIMIT 0;

-- ============================================================================
-- Expected output:
-- "SUCCESS: Table created"
--
-- If you see an error about "already exists", that's fine - it means
-- the table was already created.
-- ============================================================================
