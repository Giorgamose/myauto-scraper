# SELECT Query Issue Analysis

## Finding from GitHub Actions Log

The application ran successfully but failed during cleanup with this error:

```
[WARN] Cleanup failed (non-critical): 505, message='Invalid response status'
```

This occurred at line: `cleanup_old_listings()` trying to execute:
```sql
SELECT COUNT(*) as count FROM seen_listings WHERE created_at < ?
```

## Key Discovery

✅ **CREATE TABLE statements work** (schema initialization succeeded)
❌ **SELECT queries fail with 505 error** (cleanup failed)

This is a **Turso server-side issue**, not a client-side SSL issue!

## Critical Code Paths Using SELECT

1. **`has_seen_listing()`** (main.py line 181)
   ```python
   result = self.client.execute(
       "SELECT 1 FROM seen_listings WHERE id = ?",
       [listing_id]
   )
   ```
   This is called for EVERY listing to check if we've seen it before.

2. **`cleanup_old_listings()`** (database.py line 464)
   ```python
   count_result = self.client.execute(
       "SELECT COUNT(*) as count FROM seen_listings WHERE created_at < ?",
       [cutoff_date]
   )
   ```
   This is called at the end of each cycle.

## Why GitHub Actions Didn't Crash

The error log shows:
```
2025-11-10 05:22:26 - scraper - INFO - [OK] Found 0 listings in search results
```

Since the scraper found 0 listings:
- ✅ `has_seen_listing()` was never called (no listings to check)
- ✅ Main logic completed without needing database reads
- ❌ Cleanup tried to execute SELECT → **505 error**
- ✅ Cleanup error is non-critical → application continued
- ✅ Application exited with code 0 (success)

## The Problem

When there ARE listings found (which is the normal case):
1. Scraper finds 20 listings
2. For each listing, calls `has_seen_listing()` to check if we've seen it
3. `has_seen_listing()` tries to execute: `SELECT 1 FROM seen_listings WHERE id = ?`
4. **505 error** → Application will crash or fail

## Root Cause Hypothesis

The new Turso database (`myautocarlistings-giorgamose`) might have:

1. **Read permissions disabled** 
   - Turso might have created database in write-only mode
   - Common issue with newly created databases

2. **Database state issue**
   - Database schema exists (CREATE TABLE worked)
   - Database is rejecting SELECT operations specifically
   - Possible corrupted database or misconfiguration

3. **Turso platform issue**
   - This specific database instance might have a bug
   - Turso server rejecting SELECT on this database specifically

## What Works vs Doesn't Work

| Operation | Status | Details |
|-----------|--------|---------|
| CREATE TABLE | ✅ WORKS | Schema initialization successful |
| INSERT | ❓ UNKNOWN | Not tested yet (skipped in main flow) |
| SELECT | ❌ FAILS | Returns 505 error |
| DELETE | ❓ UNKNOWN | Not tested (cleanup failed at SELECT) |

## Immediate Actions

### 1. Test if issue affects has_seen_listing()
If scraper finds listings in next run and tries to check them:
```python
# This will be called for each listing
has_seen_listing("listing_123")  # SELECT 1 FROM seen_listings WHERE id = ?
# Expected: 505 error
```

### 2. Check Turso Dashboard
- Go to https://app.turso.tech
- Select `myautocarlistings-giorgamose` database
- Check database status
- Look for any error messages or warnings
- Check if database is in normal/active state

### 3. Possible Solutions

**Option A: Wait & Retry**
- New databases need time to fully initialize (5-30 minutes)
- Wait and retry the application

**Option B: Use Old Database**
- Switch back to old `car-listings-giorgamose` database
- If it works, new database has an issue
- If old database also fails, it's a network/Turso service issue

**Option C: Recreate Database**
- Delete `myautocarlistings-giorgamose` from Turso
- Create new database with fresh name
- Get new credentials
- Update .env.local

**Option D: Contact Turso Support**
- Turso Discord: https://discord.gg/turso
- Report: "New database can CREATE TABLE but SELECT returns 505 error"

## Testing Code

To trigger the SELECT error:

```python
import os
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv('.env.local')

db = DatabaseManager(
    os.getenv('TURSO_DATABASE_URL'),
    os.getenv('TURSO_AUTH_TOKEN')
)

# This should work
db.initialize_schema()  # CREATE TABLE ✅

# This will fail with 505
try:
    result = db.has_seen_listing("test-listing-123")  # SELECT ❌
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## Summary

- ✅ Database connection works (authentication OK)
- ✅ Database schema creation works (CREATE TABLE OK)
- ❌ Database SELECT queries fail (505 error)
- 🔴 **This is a blocking issue for production use**

The application will fail as soon as the scraper finds listings and tries to check if they've been seen before.

## Next Report

Once you test with the next run that finds listings, we'll know:
1. If SELECT queries are indeed broken
2. If it affects the main application logic
3. If we need to switch databases or contact Turso support

