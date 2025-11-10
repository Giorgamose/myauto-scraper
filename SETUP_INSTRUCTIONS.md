# MyAuto Car Listing Monitor - Setup Instructions

## Overview

The monitoring system has been migrated from direct PostgreSQL connections to **Supabase REST API**. This eliminates IPv6 connectivity issues in GitHub Actions.

## Prerequisites

- ✅ Supabase account with project: `efohkibukutjvrrhhxdn`
- ✅ GitHub repository access
- ✅ Python 3.8+ installed locally

---

## Step 1: Regenerate Your Supabase API Key

**⚠️ CRITICAL:** Your old API key was exposed. You must regenerate it immediately.

### In Supabase Dashboard:
1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project: `efohkibukutjvrrhhxdn`
3. Go to **Project Settings → API**
4. Find the **service_role** key section
5. Click the **refresh icon** to regenerate
6. Copy the **NEW** key (save it temporarily)

---

## Step 2: Create Database Tables

The REST API cannot execute CREATE TABLE statements directly. You must create the tables manually.

### Option A: Using Supabase SQL Editor (Recommended, 2 minutes)

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project: `efohkibukutjvrrhhxdn`
3. Click **SQL Editor** in the left sidebar
4. Click **+ New Query**
5. Open [`setup_database.sql`](setup_database.sql) in this repository
6. Copy the entire contents
7. Paste into the SQL Editor
8. Click **RUN**

✅ **Tables created!**

### Option B: Using psql Command Line

```bash
psql -h db.efohkibukutjvrrhhxdn.supabase.co \
     -U postgres \
     -d postgres \
     -f setup_database.sql
```

You'll be prompted for your PostgreSQL password (from `.env.local`).

---

## Step 3: Configure Local Environment

Edit `.env.local` and add your credentials:

```bash
# Supabase REST API
SUPABASE_URL=https://efohkibukutjvrrhhxdn.supabase.co
SUPABASE_API_KEY=your_new_regenerated_api_key_here

# Telegram (optional but recommended)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

---

## Step 4: Test Database Connection Locally

```bash
python test_db_connection.py
```

Expected output:
```
[*] Testing Supabase REST API connection...
[*] Using Supabase URL: https://efohkibukutjvrrhhxdn.supabase.co
[*] Using API Key: sb_secret_XXX...
[OK] Connection successful!
[OK] Database Statistics: {...}
```

---

## Step 5: Configure GitHub Secrets

Your GitHub Actions workflow needs credentials to access Supabase.

### Add GitHub Secrets:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these two secrets:

| Secret Name | Value |
|---|---|
| `SUPABASE_URL` | `https://efohkibukutjvrrhhxdn.supabase.co` |
| `SUPABASE_API_KEY` | Your new API key from Step 1 |

✅ **GitHub secrets configured!**

---

## Step 6: Test Locally

Run the monitoring cycle locally to ensure everything works:

```bash
python main.py
```

Expected output:
```
2025-11-10 10:30:00 - __main__ - INFO - [*] MyAuto Car Listing Monitor
2025-11-10 10:30:00 - __main__ - INFO - [*] Version: 1.0.0
2025-11-10 10:30:00 - __main__ - INFO - [*] Starting monitoring cycle...
2025-11-10 10:30:00 - database - INFO - [*] Checking database schema...
2025-11-10 10:30:00 - database - INFO - [OK] All required tables exist
2025-11-10 10:30:00 - __main__ - INFO - [OK] All services initialized successfully
...
[OK] Monitoring cycle completed successfully
```

---

## Step 7: Push to GitHub and Run Workflow

```bash
git add .
git commit -m "Setup: Configure Supabase REST API for GitHub Actions"
git push origin main
```

GitHub Actions will automatically trigger. Check:
- **Actions tab** → Latest workflow run
- **Logs** should show successful execution

---

## Utility Commands

### View Database Statistics

```bash
python query_db.py stats
```

Output:
```
==================================================
DATABASE STATISTICS
==================================================

Total Listings: 42
Recent Listings (24h): 3
Last Updated: 2025-11-10T10:30:00.000000
```

### View Recent Listings

```bash
python query_db.py listings 10
```

### View Specific Listing

```bash
python query_db.py listing 119084515
```

---

## Troubleshooting

### Error: "Missing database tables"

**Problem:** The REST API is connected but tables don't exist.

**Solution:**
1. Run Step 2 again: Create tables using Supabase SQL Editor
2. Verify with: `python test_db_connection.py`

### Error: "Failed to connect: SUPABASE_API_KEY not found"

**Problem:** Environment variables not set correctly.

**Solution:**
1. Check `.env.local` has `SUPABASE_API_KEY`
2. Verify value is not empty and starts with `sb_`
3. Run: `python test_db_connection.py` to debug

### GitHub Actions Still Failing

**Problem:** Workflow runs but still fails.

**Solution:**
1. Check GitHub Secrets are set correctly:
   - Go to Settings → Secrets and variables
   - Verify `SUPABASE_URL` and `SUPABASE_API_KEY` exist
2. Check workflow logs for specific error
3. Ensure tables were created (Step 2)

---

## What Changed (Summary)

| Before | After |
|---|---|
| Direct PostgreSQL via psycopg2 | Supabase REST API over HTTPS |
| IPv6 connection failures | No IPv6/IPv4 issues |
| Manual socket connections | Simple HTTP requests |
| `database.py` module | `database_rest_api.py` module |
| `DB_USER`, `DB_PASSWORD`, etc. | `SUPABASE_URL`, `SUPABASE_API_KEY` |

---

## Security Notes

⚠️ **Important:**

1. **Never commit `.env.local`** - Already in `.gitignore`
2. **GitHub Secrets are encrypted** - Safe to use in Actions
3. **Regenerate API keys regularly** - Best practice
4. **Use Role-based keys** - Use `service_role` for backend

---

## Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review GitHub Actions logs
3. Verify all 7 steps are completed
4. Check Supabase dashboard for table status

---

**Setup Complete! 🎉**

Your monitoring system is ready to run on GitHub Actions without IPv6 connectivity issues!
