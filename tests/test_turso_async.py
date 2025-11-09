#!/usr/bin/env python3
"""
Test Turso Connection with Async Support
This is the correct way to use libsql_client
"""

import asyncio
from libsql_client import AsyncClient

# Your Turso credentials
DATABASE_URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw"

async def test_turso():
    """Test Turso database connection"""

    print("[*] TURSO ASYNC CONNECTION TEST")
    print("=" * 60)

    try:
        print("\n[1] Creating async client...")
        client = AsyncClient(DATABASE_URL, auth_token=AUTH_TOKEN)
        print("[OK] Client created")

        print("\n[2] Executing test query...")
        response = await client.execute("SELECT 1 as test")
        print("[OK] Query executed!")
        print(f"    Result: {response}")

        print("\n[3] Getting database info...")
        info = await client.execute("SELECT sqlite_version() as version")
        print(f"    SQLite version: {info}")

        print("\n" + "=" * 60)
        print("[OK] SUCCESS! Turso is working correctly!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify credentials in test file")
        print("  3. Ensure database 'car-listings' exists")
        return False

    finally:
        try:
            await client.close()
        except:
            pass

async def main():
    """Main function"""
    success = await test_turso()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
