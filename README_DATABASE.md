# Database Scripts - Quick Start Guide

**Want to see your scraped car listings?** This is the guide for you.

---

## ⚡ 30-Second Setup

1. **Install library** (one time):
   ```bash
   pip install libsql-client
   ```

2. **Set your credentials** (every session):
   ```powershell
   # PowerShell
   $env:TURSO_DATABASE_URL = "libsql://your-db.turso.io"
   $env:TURSO_AUTH_TOKEN = "your-token"
   ```

3. **Test your setup**:
   ```bash
   python test_db_connection.py
   ```

4. **View your data**:
   ```bash
   python view_database.py
   ```

---

## 📚 What You Have

| File | Purpose | When to Use |
|------|---------|------------|
| **test_db_connection.py** | Verify everything works | First time setup |
| **view_database.py** | Quick overview & stats | Daily checks |
| **query_database.py** | Search & filter data | Finding specific cars |
| **db_table_view.py** | Simple list view | Quick scan |
| **SETUP_DATABASE_SCRIPTS.md** | Detailed setup guide | If you're stuck |
| **DATABASE_QUERY_GUIDE.md** | Complete reference | Deep dive into features |
| **DATABASE_SCRIPTS_SAMPLE_OUTPUT.md** | See example outputs | Understand what you'll see |

---

## 🚀 Typical Workflow

### First Time (Do Once)
```bash
# 1. Install library
pip install libsql-client

# 2. Get credentials from https://app.turso.tech

# 3. Set environment variables
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"

# 4. Test
python test_db_connection.py

# 5. View your data
python view_database.py
```

### Daily (Every Check)
```bash
# Set variables (if not permanent)
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"

# View data
python view_database.py

# Or search/filter
python query_database.py
```

---

## 📊 Your Database Contains

**31 fields per vehicle listing:**
- Vehicle info: Make, model, year, body type, color
- Engine specs: Volume, power, fuel type, transmission
- Condition: Mileage, owners, accidents, customs status
- Pricing: Price in Georgian Lari (GEL)
- Seller info: Name, phone, email, location
- Metadata: When scraped, last updated, view count

**What you're tracking:**
- 🎯 **Target**: Toyota Land Cruiser Prado (1995-2008)
- 💰 **Price range**: 11,000 - 18,000 GEL
- ⛽ **Fuel**: Diesel
- 🔧 **Transmission**: Manual
- ✅ **Customs**: Cleared

---

## 🎯 Quick Reference

### View All Your Data
```bash
python view_database.py
```
Shows: Overview, latest records, statistics, breakdowns

### Find Cheap Cars
```bash
python query_database.py
# Select option 3 (Filter by Price)
# Enter range: 11000 to 15000
```

### Find Recent Listings
```bash
python query_database.py
# Select option 6 (Last N Days)
# Enter: 1 (for today)
```

### Get Full Details of One Car
```bash
python query_database.py
# Select option 7 (Lookup by ID)
# Paste the listing ID
```

### Export for Excel
```bash
python query_database.py
# Select option 9 (Export to CSV)
# Enter filename: my_data
```

### See Records in Table Format
```bash
python db_table_view.py
```
Shows: Clean table of latest 50 records

---

## 🆘 Troubleshooting

### "TURSO_DATABASE_URL is not set"
```powershell
$env:TURSO_DATABASE_URL = "libsql://your-database.turso.io"
```
[See SETUP_DATABASE_SCRIPTS.md for detailed help]

### "libsql_client not found"
```bash
pip install libsql-client
```

### "No records found / Database is empty"
The scraper runs every 10 minutes. Wait and try again.

### "Connection refused"
Check internet connection and verify database URL is correct.

---

## 📈 Expected Data Growth

| Time | Records | Prados | Other |
|------|---------|--------|-------|
| Day 1 | 5-10 | 2-3 | 3-7 |
| Day 7 | 40-70 | 15-25 | 25-45 |
| Day 30 | 200-300 | 50-100 | 150-200 |
| Year 1 | 2000-3000 | 500-800 | 1500-2200 |

Then automatically cleaned to keep only last 365 days.

---

## 🔐 Where to Get Credentials

1. Go to **https://app.turso.tech**
2. Log in
3. Click your database **"car-listings"**
4. Copy **Database URL** (starts with `libsql://`)
5. Copy **Auth Token** (long alphanumeric string)

---

## 💡 Pro Tips

### Tip 1: Save Common Searches
If you often search for cars under 13,000 GEL, create a batch file:
```cmd
# save as check_cheap_cars.bat
@echo off
set TURSO_DATABASE_URL=your-url
set TURSO_AUTH_TOKEN=your-token
python query_database.py
```
Then run: `check_cheap_cars.bat`

### Tip 2: Daily Email Report
Use Windows Task Scheduler to run `view_database.py` daily and email results.

### Tip 3: Track Price Trends
Export to CSV monthly (`query_database.py` option 9) and compare prices over time.

### Tip 4: Alert on New Listings
Run `view_database.py` regularly and note the timestamp of latest records.

### Tip 5: Make it Permanent
Set environment variables in Windows System Settings so you don't need to set them each time.
[See SETUP_DATABASE_SCRIPTS.md section 8️⃣]

---

## 📝 Database Fields Explained

| Field | Example | Notes |
|-------|---------|-------|
| listing_id | 987654321 | Unique ID from myauto.ge |
| title | Toyota Prado 2005 | Full listing title |
| make | Toyota | Vehicle manufacturer |
| model | Land Cruiser Prado | Model name |
| year | 2005 | Model year |
| price | 17500 | In Georgian Lari |
| mileage | 145000 | In kilometers |
| fuel_type | Diesel | Petrol or Diesel |
| transmission | Manual | Manual or Automatic |
| seller_phone | +995591234567 | Seller contact |
| created_at | 2024-11-09 | When scraped |

---

## 🔗 Related Files

- **README.md** - Main project setup
- **DEPLOYMENT_GUIDE.md** - GitHub Actions setup
- **SETUP_DATABASE_SCRIPTS.md** - Detailed Windows setup
- **DATABASE_QUERY_GUIDE.md** - Complete feature reference
- **DATABASE_SCRIPTS_SAMPLE_OUTPUT.md** - See what outputs look like

---

## ✅ Checklist

- [ ] Installed libsql-client: `pip install libsql-client`
- [ ] Got Turso credentials from turso.tech
- [ ] Set TURSO_DATABASE_URL environment variable
- [ ] Set TURSO_AUTH_TOKEN environment variable
- [ ] Ran test_db_connection.py and it passed
- [ ] Ran view_database.py and saw your data

Once all checked, you're ready to use all database scripts!

---

## 🆘 Need More Help?

1. **Quick setup**: See **SETUP_DATABASE_SCRIPTS.md**
2. **See examples**: See **DATABASE_SCRIPTS_SAMPLE_OUTPUT.md**
3. **All features**: See **DATABASE_QUERY_GUIDE.md**
4. **Still stuck**: Check the relevant file for your issue

---

**Version**: 1.0.0
**Last Updated**: November 9, 2025
**Status**: Production Ready ✅
