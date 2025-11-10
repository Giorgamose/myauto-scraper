#!/usr/bin/env python3
"""
Run Turso diagnostic with environment loaded from .env.local
"""

import os
from dotenv import load_dotenv

# Load .env.local FIRST
load_dotenv('.env.local')

# Now run the diagnostic
print("[*] TURSO DATABASE CONNECTIVITY DIAGNOSTIC")
print("=" * 70)

import sys
import socket
import requests
import urllib3
from urllib.parse import urlparse

# Suppress SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

db_url = os.getenv("TURSO_DATABASE_URL", "").strip()
auth_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()

print("\n[1] CREDENTIALS CHECK")
print("-" * 70)
if db_url:
    print("[OK] TURSO_DATABASE_URL: " + db_url)
else:
    print("[ERROR] TURSO_DATABASE_URL: NOT SET")
    sys.exit(1)

if auth_token:
    print("[OK] TURSO_AUTH_TOKEN: " + auth_token[:50] + "...")
else:
    print("[ERROR] TURSO_AUTH_TOKEN: NOT SET")
    sys.exit(1)

# Parse URL
parsed = urlparse(db_url)
hostname = parsed.netloc or parsed.path.split('/')[0]
print("[OK] Parsed hostname: " + hostname)

print("\n[2] NETWORK CONNECTIVITY TEST")
print("-" * 70)
try:
    print("[*] Testing socket connection to " + hostname + ":443...")
    socket.create_connection((hostname, 443), timeout=5)
    print("[OK] Socket connection successful")
except Exception as e:
    print("[ERROR] Socket connection failed: " + str(e))
    sys.exit(1)

print("\n[3] HTTP/HTTPS CONNECTIVITY TEST")
print("-" * 70)
try:
    print("[*] Testing HTTPS request to https://" + hostname + "...")
    response = requests.get("https://" + hostname, timeout=5, verify=False)
    print("[OK] HTTPS request returned: " + str(response.status_code))
except requests.exceptions.SSLError as e:
    print("[ERROR] SSL Error (expected, continuing...): " + str(e)[:100])
except Exception as e:
    print("[WARN] Connection error: " + type(e).__name__)

print("\n[4] LIBSQL CLIENT TEST")
print("-" * 70)
try:
    print("[*] Importing libsql_client...")
    from libsql_client import create_client_sync
    print("[OK] libsql_client imported")

    print("[*] Creating client...")
    client = create_client_sync(url=db_url, auth_token=auth_token)
    print("[OK] Client created")

    print("[*] Executing query: SELECT 1...")
    result = client.execute("SELECT 1 as test")
    print("[OK] Query successful!")
    print("    Result: " + str(result))

except ImportError as e:
    print("[ERROR] Import failed: pip install libsql-client")
except Exception as e:
    print("[ERROR] " + type(e).__name__)
    print("    Message: " + str(e)[:200])

print("\n" + "=" * 70)
