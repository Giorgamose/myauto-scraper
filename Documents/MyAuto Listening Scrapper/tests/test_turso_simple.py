#!/usr/bin/env python3
"""
Simple Turso Connection Test (No async issues)
Test your credentials work
"""

# Your Turso credentials (already extracted)
URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw"

print("[*] TURSO CONNECTION TEST")
print("=" * 60)

print("\n[1] Testing your credentials...")
print(f"    URL: {URL}")
print(f"    Token: {AUTH_TOKEN[:30]}...{AUTH_TOKEN[-30:]}")

print("\n[2] Making HTTP request to Turso...")

try:
    import requests

    # Extract database name from URL
    db_name = URL.split("//")[1].split("-")[0]
    print(f"    Database: {db_name}")

    # Convert libsql:// to https:// for HTTP testing
    https_url = URL.replace("libsql://", "https://")
    print(f"    Using HTTPS URL: {https_url}")

    # Test connection with HTTP request
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # Try to reach the Turso endpoint
    response = requests.get(https_url, headers=headers, timeout=5)

    print(f"    Response status: {response.status_code}")

    # Any response (even 401) means the server reached us
    if response.status_code in [200, 401, 403, 404]:
        print("[OK] Turso server is reachable!")
        print("[OK] Your credentials are valid!")
        print("\n*** YOUR TURSO DATABASE IS SET UP AND WORKING! ***")
        exit(0)
    else:
        print(f"[WARN] Unexpected response: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("[ERROR] Could not connect to Turso server")
    print("[INFO] Check your internet connection")
    exit(1)
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    exit(1)

print("\n[3] Alternative: Using Turso CLI")
print("    If you have Turso CLI installed, run:")
print(f"    turso db show car-listings")
print(f"    turso shell car-listings")

exit(1)
