#!/usr/bin/env python3
"""
Supabase Connection Diagnostic Script
Checks if Supabase credentials are set up correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

print("=" * 60)
print("SUPABASE CONNECTION DIAGNOSTIC")
print("=" * 60)
print()

# Check 1: Environment variables
print("1️⃣  CHECKING ENVIRONMENT VARIABLES")
print("-" * 60)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

print(f"SUPABASE_URL:      {'✅ Set' if supabase_url else '❌ MISSING'}")
if supabase_url:
    print(f"  Value: {supabase_url[:50]}...")
else:
    print("  ⚠️  Required for bot to work")

print(f"SUPABASE_API_KEY:  {'✅ Set' if supabase_key else '❌ MISSING'}")
if supabase_key:
    print(f"  Value: {supabase_key[:20]}...{supabase_key[-10:]}")
else:
    print("  ⚠️  Required for bot to work")

print(f"TELEGRAM_BOT_TOKEN:{'✅ Set' if telegram_token else '❌ MISSING'}")
if telegram_token:
    print(f"  Value: {telegram_token[:20]}...{telegram_token[-5:]}")
else:
    print("  ⚠️  Required for bot to work")

print()

# Check 2: Supabase URL format
print("2️⃣  CHECKING SUPABASE URL FORMAT")
print("-" * 60)

if supabase_url:
    if "supabase.co" in supabase_url:
        print("✅ URL looks correct (contains 'supabase.co')")
        if supabase_url.startswith("https://"):
            print("✅ URL has HTTPS protocol")
        else:
            print("❌ URL should start with 'https://'")
            print(f"   Current: {supabase_url[:20]}")
    else:
        print("❌ URL doesn't look like Supabase URL")
        print(f"   Expected: https://xxxxx.supabase.co")
        print(f"   Got: {supabase_url}")
else:
    print("❌ SUPABASE_URL not set - CANNOT CONTINUE")

print()

# Check 3: API Key format
print("3️⃣  CHECKING SUPABASE API KEY FORMAT")
print("-" * 60)

if supabase_key:
    if len(supabase_key) > 50:
        print("✅ API key looks long enough (anon key is usually 100+ chars)")
    else:
        print("⚠️  API key might be too short")
        print(f"   Length: {len(supabase_key)} characters")

    if "eyJ" in supabase_key:
        print("✅ API key looks like JWT (starts with 'eyJ')")
    else:
        print("⚠️  API key doesn't look like JWT format")
else:
    print("❌ SUPABASE_API_KEY not set - CANNOT CONTINUE")

print()

# Check 4: Try to connect
print("4️⃣  ATTEMPTING SUPABASE CONNECTION")
print("-" * 60)

if supabase_url and supabase_key:
    try:
        import requests

        # Test basic connectivity
        url = f"{supabase_url}/rest/v1/user_subscriptions?limit=1"
        headers = {
            "apikey": supabase_key,
            "Content-Type": "application/json"
        }

        print(f"Testing connection to: {url[:60]}...")
        response = requests.get(url, headers=headers, timeout=5)

        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUPABASE CONNECTION SUCCESSFUL")
            data = response.json()
            print(f"   Tables accessible: YES")
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED")
            print("   Invalid API key")
            print("   Check SUPABASE_API_KEY in .env.local")
        elif response.status_code == 404:
            print("❌ TABLE NOT FOUND")
            print("   Table 'user_subscriptions' doesn't exist")
            print("   Run: supabase_schema_telegram_bot.sql in Supabase SQL Editor")
        else:
            print(f"❌ CONNECTION FAILED: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ NETWORK CONNECTION FAILED")
        print(f"   Error: {str(e)[:100]}")
        print("   Check:")
        print("   - Internet connection is working")
        print("   - SUPABASE_URL is correct")
        print("   - Firewall/proxy not blocking")
    except requests.exceptions.Timeout:
        print("❌ CONNECTION TIMEOUT")
        print("   Supabase server not responding")
        print("   Check your internet connection")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)[:100]}")
else:
    print("⏭️  SKIPPED - Missing credentials")

print()

# Check 5: Summary
print("5️⃣  SUMMARY")
print("-" * 60)

errors = []

if not supabase_url:
    errors.append("SUPABASE_URL not in .env.local")
if not supabase_key:
    errors.append("SUPABASE_API_KEY not in .env.local")
if not telegram_token:
    errors.append("TELEGRAM_BOT_TOKEN not in .env.local")

if errors:
    print("❌ ISSUES FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    print()
    print("FIX:")
    print("   1. Open .env.local in editor")
    print("   2. Add missing environment variables")
    print("   3. Save file")
    print("   4. Run this script again")
else:
    print("✅ ALL CHECKS PASSED")
    print("   Your Supabase connection should work!")

print()
print("=" * 60)
