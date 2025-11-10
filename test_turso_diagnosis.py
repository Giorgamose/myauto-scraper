#!/usr/bin/env python3
"""
Comprehensive Turso Database Connectivity Diagnostic
Tests various connection methods and SSL configurations
"""

import os
import sys
import ssl
import socket
import requests
import urllib3
from urllib.parse import urlparse

print("[*] TURSO DATABASE CONNECTIVITY DIAGNOSTIC")
print("=" * 70)

# Suppress SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read credentials from environment
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

print("\n[3] HTTP/HTTPS CONNECTIVITY TEST")
print("-" * 70)
try:
    print("[*] Testing HTTPS request to https://" + hostname + "...")
    response = requests.get("https://" + hostname, timeout=5, verify=False)
    print("[OK] HTTPS request returned: " + str(response.status_code))
except requests.exceptions.SSLError as e:
    print("[ERROR] SSL Error: " + str(e))
except Exception as e:
    print("[WARN] Connection error: " + type(e).__name__ + ": " + str(e))

print("\n[4] LIBSQL CLIENT TEST")
print("-" * 70)
try:
    print("[*] Importing libsql_client...")
    from libsql_client import create_client_sync
    print("[OK] libsql_client imported successfully")

    print("[*] Creating client with URL: " + db_url)
    client = create_client_sync(url=db_url, auth_token=auth_token)
    print("[OK] Client created successfully")

    print("[*] Executing simple query: SELECT 1...")
    result = client.execute("SELECT 1 as test")
    print("[OK] Query successful: " + str(result))

except ImportError as e:
    print("[ERROR] Import error: " + str(e))
    print("  Solution: pip install libsql-client")
except Exception as e:
    print("[ERROR] Error: " + type(e).__name__ + ": " + str(e))

print("\n[5] ENVIRONMENT CHECK")
print("-" * 70)
print("Python version: " + sys.version.split()[0])
print("Platform: " + sys.platform)

try:
    import libsql_client
    if hasattr(libsql_client, '__version__'):
        print("libsql_client version: " + libsql_client.__version__)
    else:
        print("libsql_client version: unknown")
except:
    print("libsql_client version: not found")

print("\n" + "=" * 70)
print("[!] DIAGNOSIS COMPLETE")
print("=" * 70)

print("\n[NEXT STEPS]")
print("1. If Socket connection FAILED: Network/firewall issue")
print("2. If HTTPS request FAILED: SSL certificate issue (known with libsql-client)")
print("3. If Client creation FAILED: Credentials or version issue")
print("4. If Query FAILED: Database doesn't exist or schema error")
print("\n[RECOMMENDED ACTIONS]")
print("- Try: pip install --upgrade libsql-client")
print("- Check if database exists at https://turso.tech")
print("- Verify URL format: libsql://database.aws-region.turso.io")
print("- Verify token hasn't expired")
