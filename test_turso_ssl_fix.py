#!/usr/bin/env python3
"""
Test different approaches to fix Turso SSL certificate issue
"""

import os
from dotenv import load_dotenv

load_dotenv('.env.local')

db_url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

print("[*] TESTING TURSO SSL CERTIFICATE FIXES")
print("=" * 70)

# Test 1: Check if there's a way to disable SSL verification
print("\n[1] Testing with environment variable for SSL verification...")
try:
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    from libsql_client import create_client_sync
    print("[*] Trying to create client with custom SSL context...")
    # Check if create_client_sync accepts ssl_context parameter
    import inspect
    sig = inspect.signature(create_client_sync)
    print("[*] create_client_sync parameters: " + str(list(sig.parameters.keys())))

except Exception as e:
    print("[ERROR] " + str(e)[:100])

# Test 2: Try with httpx client that disables SSL verification
print("\n[2] Checking libsql_client API...")
try:
    from libsql_client import create_client_sync
    import inspect

    # Get the source code or docstring
    print("[*] Function signature:")
    print(inspect.signature(create_client_sync))

    if create_client_sync.__doc__:
        print("\n[*] Docstring:")
        print(create_client_sync.__doc__[:500])

except Exception as e:
    print("[ERROR] " + str(e))

# Test 3: Try alternative: use async client instead
print("\n[3] Testing async client...")
try:
    from libsql_client import create_client
    print("[OK] Async client available")

    import asyncio

    async def test_async():
        print("[*] Creating async client...")
        client = await create_client(url=db_url, auth_token=auth_token)
        print("[OK] Async client created")

        print("[*] Executing query...")
        result = await client.execute("SELECT 1 as test")
        print("[OK] Query result: " + str(result))

        await client.close()

    # Don't run it yet, just show it's available
    print("[OK] Async client API available")

except Exception as e:
    print("[ERROR] " + str(e)[:100])

print("\n" + "=" * 70)
