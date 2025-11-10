-- ============================================================================
-- Telegram Bot Database Cleanup/Reset Scripts
-- ============================================================================
-- Use these scripts to delete or reset bot data in Supabase
-- Run in Supabase SQL Editor: https://supabase.com/dashboard
-- ============================================================================

-- ============================================================================
-- OPTION 1: Clear All Seen Listings (Most Common)
-- ============================================================================
-- This deletes all records from user_seen_listings table
-- Effect: Bot will treat all existing listings as "new" again
-- Use when: You want the bot to re-notify about old listings

DELETE FROM user_seen_listings;

-- Verify deletion
SELECT COUNT(*) as "Remaining seen listings" FROM user_seen_listings;

-- ============================================================================
-- OPTION 2: Clear Seen Listings for a Specific User
-- ============================================================================
-- Replace CHAT_ID with your actual chat ID (e.g., 6366712840)

DELETE FROM user_seen_listings
WHERE chat_id = CHAT_ID;

-- Verify deletion for this user
SELECT COUNT(*) as "Remaining seen listings for this user" FROM user_seen_listings
WHERE chat_id = CHAT_ID;

-- ============================================================================
-- OPTION 3: Clear Seen Listings for a Specific Search
-- ============================================================================
-- First, find the subscription ID, then delete listings from that search

-- Get all subscriptions
SELECT id, chat_id, search_url FROM user_subscriptions
WHERE is_active = true;

-- Then delete seen listings (note: this is tricky without storing subscription_id in seen_listings)
-- Alternative: Clear all and let users re-add specific searches

-- ============================================================================
-- OPTION 4: Delete All Bot Events (Logs)
-- ============================================================================
-- This clears all event history

DELETE FROM bot_events;

-- Verify deletion
SELECT COUNT(*) as "Remaining events" FROM bot_events;

-- ============================================================================
-- OPTION 5: Reset Subscriptions (Remove All)
-- ============================================================================
-- This marks all subscriptions as inactive (soft delete)

UPDATE user_subscriptions
SET is_active = false;

-- Verify
SELECT COUNT(*) as "Active subscriptions" FROM user_subscriptions
WHERE is_active = true;

-- ============================================================================
-- OPTION 6: Complete Reset (Delete Everything)
-- ============================================================================
-- WARNING: This deletes ALL data for the Telegram bot

DELETE FROM user_seen_listings;
DELETE FROM bot_events;
DELETE FROM user_subscriptions;

-- Verify all tables are empty
SELECT COUNT(*) as "Subscriptions" FROM user_subscriptions;
SELECT COUNT(*) as "Seen listings" FROM user_seen_listings;
SELECT COUNT(*) as "Events" FROM bot_events;

-- ============================================================================
-- OPTION 7: Clear Last Checked Timestamps
-- ============================================================================
-- Resets the last_checked field so bot thinks subscriptions were never checked

UPDATE user_subscriptions
SET last_checked = NULL
WHERE is_active = true;

-- Verify
SELECT id, chat_id, search_url, last_checked
FROM user_subscriptions
WHERE is_active = true;

-- ============================================================================
-- OPTION 8: View Current Data (Before Deleting)
-- ============================================================================
-- Run these SELECT statements to see what you're about to delete

-- All subscriptions
SELECT * FROM user_subscriptions ORDER BY created_at DESC;

-- All seen listings (count)
SELECT chat_id, COUNT(*) as "Seen listings"
FROM user_seen_listings
GROUP BY chat_id;

-- All events (recent)
SELECT * FROM bot_events
ORDER BY created_at DESC
LIMIT 50;

-- ============================================================================
-- SAFE CLEANUP: Delete Old Data Only
-- ============================================================================
-- Delete listings seen more than 30 days ago (doesn't delete active listings)

DELETE FROM user_seen_listings
WHERE seen_at < NOW() - INTERVAL '30 days';

-- Delete events older than 30 days
DELETE FROM bot_events
WHERE created_at < NOW() - INTERVAL '30 days';

-- ============================================================================
-- TRANSACTIONAL DELETE (Safest Method)
-- ============================================================================
-- Run this in a transaction - you can ROLLBACK if something goes wrong

BEGIN;

-- Delete all seen listings
DELETE FROM user_seen_listings;

-- If you're happy with the change, run:
-- COMMIT;

-- If you want to undo, run:
-- ROLLBACK;

-- ============================================================================
-- QUICK REFERENCE
-- ============================================================================
-- Most common use cases:

-- Clear all seen listings (bot re-notifies about old listings):
-- DELETE FROM user_seen_listings;

-- Clear data for specific user:
-- DELETE FROM user_seen_listings WHERE chat_id = 6366712840;

-- Reset all subscriptions:
-- UPDATE user_subscriptions SET is_active = false;

-- Delete everything:
-- DELETE FROM user_seen_listings;
-- DELETE FROM bot_events;
-- DELETE FROM user_subscriptions;

-- ============================================================================
