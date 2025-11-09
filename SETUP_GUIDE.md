# Setup Guide - MyAuto Car Listing Scraper

**Status:** Complete setup instructions before code implementation
**Created:** November 9, 2025

---

## ⚠️ SECURITY NOTICE

**IMPORTANT:** You've shared your Meta Developer credentials in plain text.
- Change your Meta password IMMEDIATELY
- Never share credentials in plain text again
- Use secured password managers for sensitive data
- I will NOT log into any of your accounts - you'll do all setup yourself

---

## Part 1: Turso Database Setup

### What is Turso?

**Turso** is a SQLite-as-a-service platform that provides:
- ✅ Cloud-hosted SQLite databases
- ✅ Completely free tier
- ✅ GitHub Actions integration
- ✅ No storage limits mentioned
- ✅ Perfect for your use case (tracking listing IDs)

### Step 1.1: Create Turso Account

1. Go to: **https://turso.tech**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose authentication method:
   - GitHub (recommended - easier for GitHub Actions integration)
   - Google
   - Email
4. Complete signup process
5. Verify email if required

### Step 1.2: Install Turso CLI

The Turso CLI is a command-line tool to manage your databases from your computer.

**For Windows (PowerShell - Recommended):**

Open PowerShell as Administrator and run:

```powershell
curl -sSfL https://get.tur.so/install.sh | bash
```

**Alternative (Windows Command Prompt):**

```cmd
curl -sSfL https://get.tur.so/install.sh -o install.sh
bash install.sh
```

**Verify Installation:**

Open a new PowerShell/CMD window and run:

```bash
turso --version
```

**Expected Output:**
```
turso version x.x.x
```

If you see an error like "turso: command not found", restart your computer and try again.

### Step 1.3: Authenticate with Turso

In PowerShell/CMD, run:

```bash
turso auth login
```

This will:
1. Open your browser
2. Ask you to authorize the CLI
3. Create a local authentication token
4. Remember your identity on this computer

### Step 1.4: Create Your Database

Create a database for storing seen car listings:

```bash
turso db create car-listings
```

**Expected Output:**
```
Database 'car-listings' created successfully
```

### Step 1.5: Get Connection URL

Get the database connection string:

```bash
turso db show car-listings --url
```

**Expected Output:**
```
https://car-listings-xxxxx.turso.io
```

**Save this URL** - you'll need it for GitHub Secrets and environment variables.

### Step 1.6: Generate Authentication Token

Generate a permanent token for your database:

```bash
turso db tokens create car-listings
```

**Important: This opens in your browser**
1. Click "Generate Token"
2. Copy the token (long string starting with something like `v01.xxx`)
3. **Save this token securely** - you'll only see it once!

**If you lose the token**, you can generate another one with the same command.

### Step 1.7: Verify Database Access

Test the connection with libsql (Python library):

```bash
pip install libsql-client
```

Create a test file `test_turso.py`:

```python
from libsql_client import create_client

# Replace with your values
url = "https://car-listings-xxxxx.turso.io"
auth_token = "v01.xxx_your_token_xxx"

client = create_client(database_url=url, auth_token=auth_token)

# Test connection
result = client.execute("SELECT 1 as test")
print("✅ Connection successful!")
print(result)
```

Run it:

```bash
python test_turso.py
```

**Expected Output:**
```
✅ Connection successful!
...
```

### Step 1.8: Save Credentials for GitHub Actions

You now have:
- **Database URL:** `https://car-listings-xxxxx.turso.io`
- **Auth Token:** `v01.xxx...`

Save these for GitHub Secrets (we'll add them later):
```
TURSO_DATABASE_URL=https://car-listings-xxxxx.turso.io
TURSO_AUTH_TOKEN=v01.xxx...
```

---

## Part 2: Meta Developer Configuration

### What You're Setting Up

You're creating a WhatsApp Business Account in Meta's development environment that will:
- ✅ Allow you to send WhatsApp messages
- ✅ Notify yourself about new car listings
- ✅ Cost $0.00 (Sandbox mode is free)
- ✅ Support up to 5 test phone numbers

### Important: Why I'm NOT Doing This For You

You shared your Meta account credentials. Here's why I won't use them:

1. **Security Best Practice:** Never share passwords with anyone
2. **Account Safety:** Login location changes trigger security alerts
3. **Terms of Service:** Meta may disable account for unauthorized access
4. **Accountability:** Changes you make yourself are traced to you
5. **Your Control:** You maintain full control of your account

**After these setup steps, change your Meta password immediately.**

---

### Step 2.1: Log Into Meta Developer Console

1. Go to: **https://developers.facebook.com/**
2. Log in with your credentials:
   - Email: `georgemaevsky@yahoo.com`
   - Password: `G@marjveba123`
3. Complete any 2FA if prompted
4. You should see your Dashboard

### Step 2.2: Access Your App

1. In Meta Developers dashboard, look for **"My Apps"** or **"Apps"**
2. Click on your existing app (App ID: `850466404119710`)
3. You should see the app dashboard

### Step 2.3: Add WhatsApp Product

1. In the left sidebar, find **"Add Product"** or **"Set Up"**
2. Search for "WhatsApp"
3. Click on **"WhatsApp"**
4. Click **"Set Up"**

This automatically creates:
- ✅ Test WhatsApp Business Account
- ✅ Test phone number (Meta provides)
- ✅ API credentials

### Step 2.4: Access WhatsApp Setup

1. In left sidebar, click **"WhatsApp"**
2. Click **"Getting started"** or **"API Setup"**
3. You should see:
   - From phone number (with an ID like `102123456789`)
   - Test recipient numbers area
   - API access options

### Step 2.5: Add Your Phone Number as Test Recipient

**Add Recipient Phone:**

1. In API Setup page, find **"Manage phone number list"** or **"Add Recipient"**
2. Click to expand
3. Enter your phone number: **`+995577072753`**
4. Click **"Add"** or **"Register"**

**Verify Your Phone:**

1. Check your WhatsApp on phone
2. You'll receive a message with a **6-digit verification code**
3. Copy the code
4. Return to Meta dashboard
5. Paste the code in the verification field
6. Click **"Verify"** or **"Confirm"**

**Result:** Your phone is now registered as test recipient #1 (out of 5)

### Step 2.6: Create System User for Tokens

**Go to Business Manager:**

1. Visit: **https://business.facebook.com/settings/**
2. In left sidebar, click **"Users"**
3. Click **"System Users"** (not Regular Users)
4. Click **"Add"** or **"Create System User"**

**Configure System User:**

1. **Name:** `MyAuto WhatsApp Bot` (or any name you like)
2. **Role:** Select **"Admin"** from dropdown
3. Click **"Create System User"**

**System user is now created**

### Step 2.7: Generate Permanent Access Token

1. Click on the newly created system user: `MyAuto WhatsApp Bot`
2. Find **"Generate Token"** button
3. Click it

**In the popup:**

1. **Select App:** Choose `850466404119710` from the dropdown
2. **Select Permissions:**
   - ✅ Check `whatsapp_business_messaging`
   - ✅ Check `whatsapp_business_management`
   - ✅ (Optional) Check `catalog_management`
3. **Token Expiration:** Set to "**Never**" (if available)
   - Or set to 60 days (you can renew it later)
4. Click **"Generate Token"**

**IMPORTANT: Copy this token now**
- The token only displays ONCE
- It starts with "EAA..."
- Save it safely
- You'll need it for GitHub Secrets

**Token Format Example:**
```
EAAbcd12345efgh67890ijkl...
```

### Step 2.8: Find Your Phone Number ID

**In API Setup page:**

1. Look for **"From Phone Number ID"** or **"Phone Number ID"**
2. It will be a numeric string like: `102123456789`
3. **Copy and save this** - you'll need it for GitHub Secrets

### Step 2.9: Test Your Configuration

**Create test file `test_whatsapp.py`:**

```python
import requests
import os

# Your values from Meta
PHONE_ID = "102123456789"  # Replace with your Phone ID
TOKEN = "EAA...your_token..."  # Replace with your token
TARGET_PHONE = "995577072753"  # Your phone number

def send_test_message():
    """Send a test WhatsApp message"""

    url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": TARGET_PHONE,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "🚗 Test message from MyAuto Scraper - Setup successful! ✅"
        }
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        print("✅ TEST MESSAGE SENT SUCCESSFULLY!")
    else:
        print("❌ Error sending message")

if __name__ == "__main__":
    send_test_message()
```

**Run it:**

```bash
python test_whatsapp.py
```

**Expected Result:**
- ✅ You receive a WhatsApp message: "🚗 Test message from MyAuto Scraper - Setup successful! ✅"
- ✅ Script output shows status code 200

If this works, your WhatsApp API is properly configured! 🎉

---

## Part 3: GitHub Secrets Configuration

### What Are GitHub Secrets?

GitHub Secrets are encrypted variables that:
- ✅ Store sensitive data (tokens, passwords, keys)
- ✅ Are hidden from public view
- ✅ Are only accessible to GitHub Actions workflows
- ✅ Are safer than hardcoding in your code

### Step 3.1: Collect All Secrets

Before adding to GitHub, have these values ready:

```
1. TURSO_DATABASE_URL = https://car-listings-xxxxx.turso.io
2. TURSO_AUTH_TOKEN = v01.xxx...
3. WHATSAPP_TOKEN = EAA...
4. WHATSAPP_PHONE_ID = 102123456789
5. WHATSAPP_PHONE_NUMBER = 995577072753
```

### Step 3.2: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In left sidebar, click **"Secrets and variables"**
4. Click **"Actions"**
5. Click **"New repository secret"** button

**Add each secret one at a time:**

**Secret 1: TURSO_DATABASE_URL**
- **Name:** `TURSO_DATABASE_URL`
- **Value:** `https://car-listings-xxxxx.turso.io` (from Step 1.5)
- Click **"Add secret"**

**Secret 2: TURSO_AUTH_TOKEN**
- **Name:** `TURSO_AUTH_TOKEN`
- **Value:** `v01.xxx...` (from Step 1.6)
- Click **"Add secret"**

**Secret 3: WHATSAPP_TOKEN**
- **Name:** `WHATSAPP_TOKEN`
- **Value:** `EAA...` (from Step 2.7)
- Click **"Add secret"**

**Secret 4: WHATSAPP_PHONE_ID**
- **Name:** `WHATSAPP_PHONE_ID`
- **Value:** `102123456789` (from Step 2.8)
- Click **"Add secret"**

**Secret 5: WHATSAPP_PHONE_NUMBER**
- **Name:** `WHATSAPP_PHONE_NUMBER`
- **Value:** `995577072753`
- Click **"Add secret"**

**Verify All Secrets Are Added:**

You should now see all 5 secrets listed in the Secrets page.

---

## Part 4: Database Schema Based on MyAuto Data

### Research Findings

Based on analysis of MyAuto.ge, here's the expected data structure for listings:

### Complete Database Schema

**Table 1: `seen_listings`** (Track which listings we've already notified about)

```sql
CREATE TABLE seen_listings (
    id TEXT PRIMARY KEY,                              -- Listing ID (e.g., "119084515")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When we first saw it
    last_notified_at TIMESTAMP,                       -- When we sent notification
    notified BOOLEAN DEFAULT 1                        -- Was notified about this?
);

CREATE INDEX idx_created_at ON seen_listings(created_at);
```

---

**Table 2: `vehicle_details`** (Complete car information)

```sql
CREATE TABLE vehicle_details (
    listing_id TEXT PRIMARY KEY REFERENCES seen_listings(id) ON DELETE CASCADE,

    -- VEHICLE IDENTIFICATION
    make TEXT,                          -- Toyota
    make_id INTEGER,                    -- 41
    model TEXT,                         -- Land Cruiser
    model_id INTEGER,                   -- 1109
    modification TEXT,                  -- Prado
    year INTEGER,                       -- 2001
    vin TEXT UNIQUE,                    -- Vehicle ID Number

    -- PHYSICAL CHARACTERISTICS
    body_type TEXT,                     -- SUV, Sedan, etc.
    color TEXT,                         -- Black, White, etc.
    interior_color TEXT,                -- Beige, etc.
    doors INTEGER,                      -- 4, 5, etc.
    seats INTEGER,                      -- 5, 7, etc.
    wheel_position TEXT,                -- Left, Right
    drive_type TEXT,                    -- 4WD, FWD, RWD, AWD

    -- ENGINE INFORMATION
    fuel_type TEXT,                     -- Diesel, Petrol, Hybrid, Electric
    fuel_type_id INTEGER,               -- 1=Petrol, 2=Diesel, 3=Hybrid, 4=Electric
    displacement_liters REAL,           -- 3.0
    transmission TEXT,                  -- Automatic, Manual, CVT
    power_hp INTEGER,                   -- 163
    cylinders INTEGER,                  -- 4, 6, 8, etc.

    -- CONDITION
    status TEXT,                        -- New, Used, Damaged
    mileage_km INTEGER,                 -- 250000
    mileage_unit TEXT,                  -- km, miles
    customs_cleared BOOLEAN,            -- 1=cleared, 0=not cleared
    technical_inspection_passed BOOLEAN,-- 1=passed, 0=not passed
    condition_description TEXT,         -- Excellent, Good, Fair, Poor

    -- PRICING
    price REAL,                         -- 15500
    currency TEXT,                      -- USD, GEL, EUR
    currency_id INTEGER,                -- 1=USD, 2=GEL, 3=EUR
    negotiable BOOLEAN,                 -- true/false
    installment_available BOOLEAN,      -- true/false
    exchange_possible BOOLEAN,          -- true/false

    -- SELLER INFORMATION
    seller_type TEXT,                   -- individual, dealer, autosalon
    seller_name TEXT,                   -- John Doe
    seller_phone TEXT,                  -- +995555123456
    location TEXT,                      -- Tbilisi
    location_id INTEGER,                -- 2
    is_dealer BOOLEAN,                  -- true/false
    dealer_id INTEGER,                  -- NULL if individual

    -- MEDIA
    primary_image_url TEXT,             -- First image URL
    photo_count INTEGER,                -- 12
    video_url TEXT,                     -- Video URL if available

    -- METADATA
    posted_date TIMESTAMP,              -- 2024-11-09T10:30:00Z
    last_updated TIMESTAMP,             -- When listing was last updated
    url TEXT,                           -- Full listing URL
    view_count INTEGER,                 -- 1247
    is_vip BOOLEAN,                     -- VIP listing?
    is_featured BOOLEAN                 -- Featured listing?
);

CREATE INDEX idx_year ON vehicle_details(year);
CREATE INDEX idx_price ON vehicle_details(price);
CREATE INDEX idx_make_model ON vehicle_details(make, model);
CREATE INDEX idx_location ON vehicle_details(location_id);
CREATE INDEX idx_posted_date ON vehicle_details(posted_date);
```

---

**Table 3: `search_configurations`** (Store your search URLs)

```sql
CREATE TABLE search_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                          -- "Toyota Land Cruiser Prado"
    search_url TEXT,                    -- Full search URL
    vehicle_make TEXT,                  -- Toyota
    vehicle_model TEXT,                 -- Land Cruiser
    year_from INTEGER,                  -- 1995
    year_to INTEGER,                    -- 2008
    price_from REAL,                    -- 11000
    price_to REAL,                      -- 18000
    currency_id INTEGER,                -- 1=USD
    is_active BOOLEAN DEFAULT 1,        -- Is this search enabled?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMP           -- When did we last check this search?
);
```

---

**Table 4: `notifications_sent`** (Track notifications)

```sql
CREATE TABLE notifications_sent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id TEXT REFERENCES seen_listings(id),
    notification_type TEXT,            -- new_listing, no_listings, error
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    whatsapp_message_id TEXT,          -- Message ID from Meta API
    success BOOLEAN                     -- Did it send successfully?
);

CREATE INDEX idx_listing_notification ON notifications_sent(listing_id, sent_at);
CREATE INDEX idx_sent_at ON notifications_sent(sent_at);
```

---

### Data Retention Policy

Delete listings older than 1 year:

```sql
DELETE FROM seen_listings
WHERE created_at < datetime('now', '-1 year');
```

Run this once per month (can be automated in main script).

---

## Part 5: Verification Checklist

Before moving to code implementation, verify:

### Turso Setup ✅
- [ ] Turso account created
- [ ] CLI installed and authenticated
- [ ] Database `car-listings` created
- [ ] Connection URL obtained
- [ ] Auth token generated and saved
- [ ] Test connection successful
- [ ] Credentials saved for GitHub

### Meta WhatsApp Setup ✅
- [ ] Logged into Meta Developer Console
- [ ] WhatsApp product added
- [ ] Phone number (+995577072753) registered
- [ ] Phone number verified (code received)
- [ ] System user created
- [ ] Access token generated
- [ ] Phone ID obtained
- [ ] Test message sent successfully

### GitHub Secrets Setup ✅
- [ ] 5 secrets added (TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, WHATSAPP_PHONE_NUMBER)
- [ ] All secrets visible in GitHub Secrets page
- [ ] No hardcoded secrets in code files

### Documentation ✅
- [ ] Plan.md updated with verified information
- [ ] Setup guide completed
- [ ] Database schema finalized
- [ ] All credentials securely stored

---

## ⚠️ FINAL SECURITY REMINDER

**Change Your Meta Password Immediately:**

Since you shared your password in plain text, change it now:

1. Go to: **https://www.facebook.com/settings/**
2. Click **"Security and Login"**
3. Click **"Change Password"**
4. Enter old password and new password
5. Save

**New password should:**
- ✅ Be at least 16 characters
- ✅ Contain uppercase + lowercase + numbers + symbols
- ✅ NOT be reused from other accounts
- ✅ Be stored in a password manager (LastPass, 1Password, Bitwarden, etc.)

---

## What's Next?

Once you complete all steps above and verify everything works:

1. ✅ All services set up (Turso, WhatsApp, GitHub)
2. ✅ All credentials secured (GitHub Secrets)
3. ✅ Database schema ready
4. ✅ Test messages working

**I will then generate:**
- Complete Python code for scraper
- Database initialization script
- Notification formatting
- GitHub Actions workflow
- Full project structure
- README with usage instructions

---

**Status:** Ready for setup
**Next:** Complete setup steps 1-5, then notify when ready for code generation

