#!/usr/bin/env python3
"""
Test Turso Connection - Synchronous Version
This uses ClientSync which doesn't require async/await
"""

from libsql_client import create_client_sync

# Your Turso credentials
DATABASE_URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw"

def main():
    """Test Turso database connection"""

    print("[*] TURSO SYNCHRONOUS CONNECTION TEST")
    print("=" * 60)

    try:
        print("\n[1] Creating sync client...")
        client = create_client_sync(url=DATABASE_URL, auth_token=AUTH_TOKEN)
        print("[OK] Client created")

        print("\n[2] Executing test query...")
        response = client.execute("SELECT 1 as test")
        print("[OK] Query executed!")
        print(f"    Result: {response}")

        print("\n[3] Getting database info...")
        info = client.execute("SELECT sqlite_version() as version")
        print(f"    SQLite version: {info}")

        print("\n[4] Creating test table...")
        client.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id INTEGER PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Test table created")

        print("\n[5] Inserting test data...")
        client.execute(
            "INSERT INTO test_connection (message) VALUES (?)",
            ["[OK] Connection working!"]
        )
        print("[OK] Test data inserted")

        print("\n[6] Reading test data...")
        result = client.execute("SELECT * FROM test_connection LIMIT 1")
        print(f"    Data: {result}")

        print("\n" + "=" * 60)
        print("[OK] SUCCESS! TURSO DATABASE IS FULLY OPERATIONAL!")
        print("=" * 60)
        print("\nYour database credentials are valid and working.")
        print("Ready to proceed with scraper implementation!")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify credentials are correct")
        print("  3. Ensure database 'car-listings' exists at turso.tech")
        print("  4. Try: pip install --upgrade libsql-client")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
