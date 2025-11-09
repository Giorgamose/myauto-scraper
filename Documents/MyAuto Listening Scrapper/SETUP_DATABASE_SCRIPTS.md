# Setup Database Scripts - Windows Quick Guide

This guide helps you set up and use the database query scripts on Windows.

---

## 1️⃣ Prerequisites

Before running any database scripts, you need:
- Python 3.7+ (check with `python --version`)
- Turso database credentials
- libsql-client library

---

## 2️⃣ Install Required Library

Open PowerShell or Command Prompt and run:

```bash
pip install libsql-client
```

**Expected Output:**
```
Successfully installed libsql-client-0.4.0
```

---

## 3️⃣ Get Your Turso Credentials

These are your database login credentials - you'll need them for the next step.

### Steps:
1. Go to https://app.turso.tech
2. Log in with your account
3. Click on your database "car-listings"
4. Copy the **Database URL** (looks like: `libsql://xxx.turso.io`)
5. Copy the **Auth Token** (long alphanumeric string)

### Example:
```
Database URL: libsql://car-listings-abc123.turso.io
Auth Token:  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 4️⃣ Set Environment Variables (Windows)

You must set two environment variables before running the scripts.

### Option A: Using PowerShell (Recommended)

Open PowerShell and paste these commands (replace with YOUR values):

```powershell
$env:TURSO_DATABASE_URL = "libsql://your-database.turso.io"
$env:TURSO_AUTH_TOKEN = "your-auth-token-here"
```

**Verify they're set:**
```powershell
Write-Host $env:TURSO_DATABASE_URL
Write-Host $env:TURSO_AUTH_TOKEN
```

You should see your database URL and token printed.

### Option B: Using Command Prompt (CMD)

Open Command Prompt and paste these commands (replace with YOUR values):

```cmd
set TURSO_DATABASE_URL=libsql://your-database.turso.io
set TURSO_AUTH_TOKEN=your-auth-token-here
```

**Verify they're set:**
```cmd
echo %TURSO_DATABASE_URL%
echo %TURSO_AUTH_TOKEN%
```

You should see your database URL and token printed.

### ⚠️ Important Notes:
- These environment variables are **temporary** - they only exist in the current terminal session
- **For PowerShell**: You might get an error about script execution. If so, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Make sure the terminal is in the project directory** before running scripts:
  ```powershell
  cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"
  ```

---

## 5️⃣ Test Your Connection

Before running the full scripts, test your setup:

```bash
python test_db_connection.py
```

### Expected Success Output:
```
======================================================================
TURSO DATABASE CONNECTION TEST
======================================================================

[STEP 1] Checking environment variables...
----------------------------------------------------------------------
[OK] TURSO_DATABASE_URL is set
     libsql://car-listings-abc123.turso.io...
[OK] TURSO_AUTH_TOKEN is set
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[STEP 2] Checking libsql_client library...
----------------------------------------------------------------------
[OK] libsql_client is installed

[STEP 3] Connecting to Turso database...
----------------------------------------------------------------------
[OK] Connected to Turso database

[STEP 4] Running test query...
----------------------------------------------------------------------
[OK] Query successful
     Records in database: 42

======================================================================
SUCCESS! YOUR SETUP IS CORRECT
======================================================================

You can now use:
  • python view_database.py       - View overview & statistics
  • python query_database.py      - Advanced filtering & search
  • python db_table_view.py       - Simple table view

Start with: python view_database.py
```

### If Test Fails:

**Error: "TURSO_DATABASE_URL is not set"**
- You didn't set the environment variable
- Run the commands in Step 4 again
- Make sure to include the entire URL: `libsql://...`

**Error: "libsql_client not found"**
- Run: `pip install libsql-client`
- Then try again

**Error: "Could not connect to database"**
- Check database URL is correct (from turso.tech)
- Check auth token is correct
- Verify internet connection
- Make sure database exists in turso.tech dashboard

---

## 6️⃣ Run the Database Scripts

Once the test passes, you can use the three main scripts:

### Script 1: View Database Overview
```bash
python view_database.py
```
Shows quick overview with statistics, latest records, and breakdown by vehicle type.
**Use this**: Daily to check for new listings

### Script 2: Advanced Query Tool
```bash
python query_database.py
```
Interactive menu with 9 filtering options:
1. All records (latest)
2. Toyota Prado only
3. Filter by price range
4. Filter by year range
5. Filter by make
6. Records from last N days
7. Lookup specific listing
8. Show all records
9. Export to CSV

**Use this**: When you need to find specific listings

### Script 3: Simple Table View
```bash
python db_table_view.py
```
Shows 50 latest records in table format for quick scanning.
**Use this**: For quick visual check of recent additions

---

## 7️⃣ Quick Workflow

### First Time Setup (Do This Once):
1. ✅ Install libsql-client: `pip install libsql-client`
2. ✅ Get credentials from turso.tech
3. ✅ Set environment variables (copy-paste from Step 4)
4. ✅ Run test: `python test_db_connection.py`

### Daily Usage:
1. Open PowerShell/CMD in project directory
2. Set environment variables (or skip if using persistent method)
3. Run: `python view_database.py`
4. Or: `python query_database.py` if you need to search

### Full Example (PowerShell):
```powershell
# Go to project directory
cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"

# Set environment variables
$env:TURSO_DATABASE_URL = "libsql://your-db.turso.io"
$env:TURSO_AUTH_TOKEN = "your-token-here"

# Test connection
python test_db_connection.py

# View database (if test passed)
python view_database.py
```

---

## 8️⃣ Make It Permanent (Optional)

If you want the environment variables to persist:

### Windows System Environment Variables:
1. Open Start Menu
2. Search for "Environment Variables"
3. Click "Edit the system environment variables"
4. Click "Environment Variables..." button
5. Click "New..." under "User variables"
6. Add:
   - Variable name: `TURSO_DATABASE_URL`
   - Variable value: `libsql://your-db.turso.io`
7. Click OK
8. Repeat steps 5-7 for `TURSO_AUTH_TOKEN`
9. **Close and reopen PowerShell/CMD** for changes to take effect

Then you can run scripts without setting variables each time:
```powershell
cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"
python view_database.py
```

---

## 9️⃣ Troubleshooting

### "ModuleNotFoundError: No module named 'libsql_client'"
**Solution**: Install the package:
```bash
pip install libsql-client
```

### "TURSO_DATABASE_URL is not set"
**Solution**: Set the environment variable:
```powershell
$env:TURSO_DATABASE_URL = "your-url"
```

### "Connection refused" or "timeout"
**Solution**:
1. Check internet connection
2. Verify database URL is correct
3. Verify database exists in turso.tech dashboard
4. Try again in a few moments

### "No records found"
**Solution**:
- Scraper might not have run yet (runs every 10 minutes)
- Wait 10 minutes and try again
- Check if GitHub Actions is running (check Actions tab)

### "Certificate verify failed"
**Solution**:
- This is an SSL issue. Run:
  ```bash
  pip install --upgrade certifi
  ```

---

## 🔟 Database Scripts Reference

| Script | Purpose | Best For |
|--------|---------|----------|
| **test_db_connection.py** | Validate setup | First time setup |
| **view_database.py** | Dashboard overview | Daily checks |
| **query_database.py** | Advanced filtering | Finding specific cars |
| **db_table_view.py** | Simple table view | Quick scan |

---

## Next Steps

1. **Run test_db_connection.py** - Verify your setup works
2. **Run view_database.py** - See all your scraped records
3. **Run query_database.py** - Filter by your criteria
4. **Export to CSV** - Use option 9 for analysis in Excel

---

## Data Availability

The scraper runs every 10 minutes from GitHub Actions:
- **First day**: 5-10 records
- **After 1 week**: 40-70 records
- **After 1 month**: 200-300 records
- **After 1 year**: 2000-3000 records (then auto-cleaned to keep last 365 days)

Each record includes 31 fields:
- Vehicle info (make, model, year, etc.)
- Pricing (price, currency)
- Specifications (engine, transmission, fuel, etc.)
- Condition (mileage, owners, accidents)
- Seller info (name, phone, location)

---

## Support

For detailed information, see:
- **DATABASE_QUERY_GUIDE.md** - Complete feature documentation
- **README.md** - General project setup
- **DEPLOYMENT_GUIDE.md** - GitHub Actions setup

---

**Version**: 1.0.0
**Last Updated**: November 9, 2025
**Platform**: Windows (PowerShell / Command Prompt)
