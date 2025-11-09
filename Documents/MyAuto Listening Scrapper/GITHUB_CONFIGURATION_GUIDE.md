# GitHub Configuration Guide - Complete Setup

## 🎯 Overview

This guide will take you through configuring your GitHub repository to run the MyAuto scraper automatically. Everything is done through the GitHub web interface - no command line needed!

**Time required**: 15 minutes
**Current status**: Code pushed to GitHub ✅

---

## ✅ Step 1: Add GitHub Secrets (10 minutes)

Your credentials are stored locally in `.env.local`. Now we'll add them to GitHub as "Secrets" so the automated workflow can access them.

### 1.1 Open Secrets Page

1. Go to: https://github.com/Giorgamose/myauto-scraper
2. Click on **Settings** tab
3. In left sidebar, click: **Secrets and variables** → **Actions**

You'll see a page that says "No secrets yet"

### 1.2 Add Secret #1: TURSO_DATABASE_URL

Click **"New repository secret"** button

**Name**: `TURSO_DATABASE_URL` (copy exactly)

**Value**: Copy from your `.env.local`:
```
libsql://car-listings-giorgamose.aws-eu-west-1.turso.io
```

Click **Add secret** ✅

### 1.3 Add Secret #2: TURSO_AUTH_TOKEN

Click **"New repository secret"** button again

**Name**: `TURSO_AUTH_TOKEN` (copy exactly)

**Value**: Copy the full token from your `.env.local`:
```
eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw
```

Click **Add secret** ✅

### 1.4 Add Secret #3: TELEGRAM_BOT_TOKEN

Click **"New repository secret"** button

**Name**: `TELEGRAM_BOT_TOKEN` (copy exactly)

**Value**: Copy from your `.env.local`:
```
8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4
```

Click **Add secret** ✅

### 1.5 Add Secret #4: TELEGRAM_CHAT_ID

Click **"New repository secret"** button

**Name**: `TELEGRAM_CHAT_ID` (copy exactly)

**Value**: Copy from your `.env.local`:
```
6366712840
```

Click **Add secret** ✅

### 1.6 Verify All 4 Secrets

You should now see:
- ✅ TELEGRAM_BOT_TOKEN
- ✅ TELEGRAM_CHAT_ID
- ✅ TURSO_AUTH_TOKEN
- ✅ TURSO_DATABASE_URL

All 4 should be listed on the Secrets page.

---

## ✅ Step 2: Enable GitHub Actions (2 minutes)

### 2.1 Open Actions Tab

1. Go to: https://github.com/Giorgamose/myauto-scraper
2. Click on **Actions** tab

You'll see a message "You don't have any workflow runs yet"

### 2.2 Enable Workflows

Click the button: **"I understand my workflows, go ahead and enable them"**

This enables the automated 10-minute schedule.

---

## ✅ Step 3: Run First Test (5 minutes)

### 3.1 Trigger Manual Workflow

1. On the **Actions** tab, click **MyAuto Car Listing Monitor** (in the left sidebar)
2. Click **Run workflow** dropdown button
3. In the dropdown, click **Run workflow** button
4. Wait 5-10 seconds...
5. You'll see a new workflow run appear

### 3.2 Monitor the Workflow

The workflow will show:
- Yellow circle = Running
- Green checkmark = Success
- Red X = Failed

Click on the workflow run to see detailed logs.

**Expected steps**:
```
✓ Checkout repository
✓ Set up Python 3.11
✓ Cache pip packages
✓ Install dependencies
✓ Download previous database state
✓ Restore database artifact
✓ Run car listing monitor         (This is the main scraper)
✓ Prepare database artifact
✓ Upload database state
✓ Log workflow completion
```

### 3.3 Verify Success

Once the workflow completes:
- Green checkmark = Success ✅
- Takes ~1-2 minutes
- Data is being scraped to your Turso database
- Telegram notification should be sent if matches found

---

## ✅ Step 4: Verify on Your Local Machine (5 minutes)

After the workflow completes successfully, verify the data was saved.

### 4.1 Set Local Environment Variables

Open PowerShell and set:

```powershell
$env:TURSO_DATABASE_URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
$env:TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw"
```

### 4.2 Test Database Connection

```bash
python test_db_connection.py
```

Expected output:
```
[OK] TURSO_DATABASE_URL is set
[OK] TURSO_AUTH_TOKEN is set
[OK] libsql_client is installed
[OK] Connected to Turso database
[OK] Query successful
     Records in database: X (should be > 0)

SUCCESS! YOUR SETUP IS CORRECT
```

### 4.3 View Database

```bash
python view_database.py
```

You should see:
- Total records count
- Latest 5 records
- Statistics
- Toyota Prado breakdown
- Price/year analysis

---

## 🔄 Step 5: What Happens Next (Automatic)

Once everything is configured, the scraper runs automatically:

### Every 10 Minutes
- GitHub Actions triggers the workflow
- Scraper runs and collects listings
- Data saved to Turso database
- Telegram notifications sent if matches

### Every Day
- ~144 scraping cycles
- 10-20 new listings expected
- Growing database of cars

### Every Week
- ~40-70 unique listings
- Enough data for analysis
- Price trends visible

### Daily Monitoring
```bash
python view_database.py  # Check latest data
python query_database.py # Search specific criteria
```

---

## 📊 Checklist

After following all steps, verify:

- [ ] You can see Settings page
- [ ] You can see Secrets and variables section
- [ ] All 4 secrets are added:
  - [ ] TURSO_DATABASE_URL
  - [ ] TURSO_AUTH_TOKEN
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] TELEGRAM_CHAT_ID
- [ ] Actions tab shows workflows enabled
- [ ] Manual workflow run completed (green checkmark)
- [ ] Local `python view_database.py` shows records

---

## 🆘 Troubleshooting

### "Secrets not found" Error

**Problem**: Workflow fails with "TURSO_DATABASE_URL is not set"

**Solution**:
1. Go to Settings → Secrets and variables → Actions
2. Verify all 4 secret names are EXACTLY correct (case-sensitive)
3. Make sure values are not empty
4. Try running workflow again

### "Connection timeout" Error

**Problem**: Workflow says "Cannot connect to Turso"

**Solution**:
1. Usually temporary network issue
2. GitHub Actions will automatically retry
3. Wait 5 minutes and run workflow manually again
4. Check that database URL and token are correct (copy from `.env.local`)

### Workflow Timeout

**Problem**: Workflow takes longer than 10 minutes

**Solution**:
1. Each run should take 30-90 seconds
2. If taking longer, check GitHub Actions logs
3. Look for step that's slow

### No Records After First Run

**Problem**: Database shows 0 records

**Solution**:
1. Check workflow logs for errors
2. Make sure `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` are correct
3. Verify they were copied completely (no missing parts)
4. Try manual workflow trigger again

---

## 📞 Help Resources

- **Turso Docs**: https://docs.turso.tech
- **GitHub Actions Docs**: https://docs.github.com/actions
- **GitHub Secrets Docs**: https://docs.github.com/actions/security-guides/encrypted-secrets
- **Telegram Bot Docs**: https://core.telegram.org/bots

---

## ✅ Next Steps After Configuration

1. ✅ Secrets added
2. ✅ Actions enabled
3. ✅ First run successful
4. ✅ Data verified locally
5. ➡️ **Let it run automatically** (every 10 minutes)
6. ➡️ **Check daily**: `python view_database.py`
7. ➡️ **Export weekly**: `python query_database.py` → Option 9

---

## 🎉 Timeline

Once configured, here's what to expect:

| Time | Action | Expected Result |
|------|--------|-----------------|
| **Now** | Add secrets & enable Actions | Setup complete |
| **First run (1-2 min)** | Manual trigger | 1-3 listings scraped |
| **Hour 1** | 6 automatic cycles | 6-18 listings total |
| **Day 1** | 144 cycles | 10-20 listings |
| **Day 7** | ~1000 cycles | 40-70 listings |
| **Day 30** | ~4300 cycles | 200-300 listings |

---

**Version**: 1.0.0
**Date**: November 9, 2025
**Status**: Ready to Configure ✅
