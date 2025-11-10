#!/usr/bin/env python3
"""
Test Turso with HTTP protocol instead of WebSocket
"""

import os
from dotenv import load_dotenv

load_dotenv('.env.local')

db_url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

print("[*] TESTING TURSO WITH HTTP PROTOCOL")
print("=" * 70)

# Convert URL from libsql:// to https://
if db_url.startswith("libsql://"):
    http_url = "https://" + db_url[9:]  # Replace libsql:// with https://
else:
    http_url = db_url

print("\n[1] ORIGINAL URL (WebSocket):")
print("    " + db_url)

print("\n[2] HTTP URL ALTERNATIVE:")
print("    " + http_url)

print("\n[3] TESTING WITH ORIGINAL WEBSOCKET URL:")
try:
    from libsql_client import create_client_sync
    print("[*] Creating client with: " + db_url)
    client = create_client_sync(url=db_url, auth_token=auth_token)
    print("[OK] Client created")

    print("[*] Executing SELECT 1...")
    result = client.execute("SELECT 1 as test")
    print("[OK] SUCCESS! Result: " + str(result))

except Exception as e:
    error_msg = str(e)
    if "SSLCertVerificationError" in error_msg or "SSL" in error_msg:
        print("[SSL ERROR] " + error_msg[:150])
        print("\n[4] TESTING WITH HTTP URL:")

        try:
            client = create_client_sync(url=http_url, auth_token=auth_token)
            print("[OK] Client created with HTTP URL")

            result = client.execute("SELECT 1 as test")
            print("[OK] SUCCESS WITH HTTP! Result: " + str(result))
            print("\n[SOLUTION] Use HTTP URL instead of libsql:// URL")
            print("           HTTP URL: " + http_url)

        except Exception as e2:
            print("[ERROR] HTTP also failed: " + str(e2)[:150])
    else:
        print("[ERROR] " + error_msg[:150])

print("\n" + "=" * 70)
