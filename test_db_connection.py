#!/usr/bin/env python3
"""
Test Turso Database Connection

Run this FIRST before using view_database.py, query_database.py, or db_table_view.py
This script validates that your environment variables are correctly set.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("TURSO DATABASE CONNECTION TEST")
print("="*70 + "\n")

# Step 1: Check environment variables
print("[STEP 1] Checking environment variables...")
print("-" * 70)

TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')

if not TURSO_DATABASE_URL:
    print("[FAILED] TURSO_DATABASE_URL is not set")
    print("\nTo fix this:")
    print("1. Go to https://app.turso.tech")
    print("2. Select your database 'car-listings'")
    print("3. Copy the Database URL")
    print("4. Set the environment variable:\n")
    print("   PowerShell: $env:TURSO_DATABASE_URL = 'your-url'")
    print("   CMD:        set TURSO_DATABASE_URL=your-url\n")
    sys.exit(1)

if not TURSO_AUTH_TOKEN:
    print("[FAILED] TURSO_AUTH_TOKEN is not set")
    print("\nTo fix this:")
    print("1. Go to https://app.turso.tech")
    print("2. Select your database 'car-listings'")
    print("3. Copy the Auth Token")
    print("4. Set the environment variable:\n")
    print("   PowerShell: $env:TURSO_AUTH_TOKEN = 'your-token'")
    print("   CMD:        set TURSO_AUTH_TOKEN=your-token\n")
    sys.exit(1)

print("[OK] TURSO_DATABASE_URL is set")
print(f"     {TURSO_DATABASE_URL[:50]}...")
print("[OK] TURSO_AUTH_TOKEN is set")
print(f"     {TURSO_AUTH_TOKEN[:20]}...\n")

# Step 2: Check if libsql_client is installed
print("[STEP 2] Checking libsql_client library...")
print("-" * 70)

try:
    from libsql_client import create_client_sync
    print("[OK] libsql_client is installed\n")
except ImportError:
    print("[FAILED] libsql_client not found")
    print("\nTo fix this, install the required package:")
    print("   pip install libsql-client\n")
    sys.exit(1)

# Step 3: Attempt connection
print("[STEP 3] Connecting to Turso database...")
print("-" * 70)

try:
    client = create_client_sync(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )
    print("[OK] Connected to Turso database\n")
except Exception as e:
    print(f"[FAILED] Could not connect to database: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify Database URL is correct (starts with libsql://)")
    print("2. Verify Auth Token is correct (long string)")
    print("3. Check internet connection")
    print("4. Verify database exists in https://app.turso.tech\n")
    sys.exit(1)

# Step 4: Test query
print("[STEP 4] Running test query...")
print("-" * 70)

try:
    result = client.execute("SELECT COUNT(*) as record_count FROM vehicle_details")
    if result.rows:
        count = result.rows[0][0]
        print(f"[OK] Query successful")
        print(f"     Records in database: {count}\n")
    else:
        print("[OK] Query successful (no records yet)")
        print("     The database is ready, but the scraper hasn't populated it yet.")
        print("     The scraper runs every 10 minutes and will add records soon.\n")
except Exception as e:
    print(f"[FAILED] Query error: {str(e)}")
    print("\nThis usually means:")
    print("1. Database doesn't have the required tables yet")
    print("2. Or the scraper hasn't run yet\n")
    sys.exit(1)

# Success!
print("="*70)
print("SUCCESS! YOUR SETUP IS CORRECT")
print("="*70)
print("\nYou can now use:")
print("  • python view_database.py       - View overview & statistics")
print("  • python query_database.py      - Advanced filtering & search")
print("  • python db_table_view.py       - Simple table view")
print("\nStart with: python view_database.py\n")
