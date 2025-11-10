-- ============================================================================
-- Table: bot_events
-- Logs all bot interactions for debugging and monitoring
-- ============================================================================
-- Run this SQL in Supabase SQL Editor to create the table
-- ============================================================================

CREATE TABLE IF NOT EXISTS bot_events (
    id BIGSERIAL PRIMARY KEY,

    -- Telegram chat ID
    chat_id BIGINT NOT NULL,

    -- Type of event (e.g., "subscription_added", "command_executed", etc.)
    event_type TEXT NOT NULL,

    -- Additional event data as JSON (flexible format for different events)
    event_data JSONB,

    -- When event occurred
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bot_events_chat_id
    ON bot_events(chat_id);

CREATE INDEX IF NOT EXISTS idx_bot_events_event_type
    ON bot_events(event_type);

CREATE INDEX IF NOT EXISTS idx_bot_events_created_at
    ON bot_events(created_at DESC);

-- Verify table was created
SELECT * FROM bot_events LIMIT 0;

-- ============================================================================
-- Expected output:
-- "SUCCESS: Table created"
--
-- If you see an error about "already exists", that's fine - it means
-- the table was already created.
--
-- This table is used for logging and debugging bot activity.
-- Examples of events logged:
-- - "subscription_added" - when user adds a search
-- - "subscription_deleted" - when user removes a search
-- - "subscriptions_cleared" - when user clears all searches
-- - "command_executed" - when any command is processed
-- - "error_occurred" - when an error happens
-- ============================================================================
