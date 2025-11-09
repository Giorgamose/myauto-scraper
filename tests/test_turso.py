#!/usr/bin/env python3
"""
Test Turso Database Connection
Fixed version with correct libsql_client API
"""

import os
import sys

# Your Turso credentials
URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjI2NzQ1MzIsImlkIjoiOTMxMDMzMzQ3LWY3Y2MtNDliZi05MmZkLTMzZWYyNDJmNzhmYiIsInJpZCI6IjNjNzAwMTg2LWYxN2YtNGRkMy05MjFkLTlhYjRiODA5ZmRkZCJ9.pRel8ta6Sw52ze8CJeohD2YOStrARJDUvcqqSWxkXEty3Zb2awAsI4f4Ao1f4b8vxVDBdDCubN8_GwDO7F-7Dw"

def test_turso_cli():
    """Test using Turso CLI (recommended)"""
    print("=" * 60)
    print("Testing Turso with CLI")
    print("=" * 60)

    import subprocess

    try:
        # List databases
        print("\n[1] Checking if database exists...")
        result = subprocess.run(
            ["turso", "db", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("[OK] Turso CLI working!")
            print(f"\nYour databases:\n{result.stdout}")

            # Get database URL
            print("\n[2] Getting database URL...")
            result = subprocess.run(
                ["turso", "db", "show", "car-listings", "--url"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                url = result.stdout.strip()
                print(f"[OK] Database URL: {url}")

                # Get token
                print("\n[3] Your connection details are ready!")
                print(f"   URL: {url}")
                print(f"   Token: {AUTH_TOKEN[:20]}...{AUTH_TOKEN[-20:]}")

                print("\n[OK] YOUR TURSO SETUP IS WORKING!")
                return True
            else:
                print(f"[ERROR] Error getting URL: {result.stderr}")
                return False
        else:
            print(f"[ERROR] Error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("[ERROR] Turso CLI not found. Install it first:")
        print("   curl -sSfL https://get.tur.so/install.sh | bash")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_libsql_client():
    """Test using libsql_client library (alternative)"""
    print("\n" + "=" * 60)
    print("Testing with libsql_client")
    print("=" * 60)

    try:
        from libsql_client import create_client

        print(f"\n[*] Connecting to Turso...")

        # Try correct parameter names
        client = create_client(url=URL, auth_token=AUTH_TOKEN)

        print("[OK] Connected successfully!")

        # Test query
        print("[*] Running test query...")
        result = client.execute("SELECT 1 as test")

        print("[OK] Query executed!")
        print(f"Result: {result}")

        return True

    except TypeError as e:
        print(f"[ERROR] Parameter error: {e}")
        print("\n[*] Troubleshooting:")
        print("   The parameter names might be different.")
        print("   Let's check what the actual API expects...")

        # Try to help diagnose
        try:
            from libsql_client import create_client
            import inspect

            sig = inspect.signature(create_client)
            print(f"\n   Actual signature: create_client{sig}")

        except Exception as diag_e:
            print(f"   Could not inspect: {diag_e}")

        return False

    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return False

def main():
    """Run tests"""
    print("\n*** TURSO CONNECTION TEST ***\n")

    # Try CLI first (most reliable)
    cli_success = test_turso_cli()

    if cli_success:
        print("\n" + "=" * 60)
        print("[OK] SUCCESS! Your Turso setup is working!")
        print("=" * 60)
        print("\nYou can now:")
        print("  - Use: turso shell car-listings")
        print("  - View schema: turso shell car-listings '.schema'")
        print("  - Query data: turso shell car-listings 'SELECT * FROM ...'")
        print("=" * 60)
        return 0

    print("\n[WARN] CLI test failed, trying libsql_client...")
    lib_success = test_libsql_client()

    if lib_success:
        print("\n[OK] libsql_client connection works!")
        return 0
    else:
        print("\n[ERROR] Both tests failed. Troubleshooting:")
        print("\n1. Check Turso CLI is installed:")
        print("   turso --version")
        print("\n2. Check you're authenticated:")
        print("   turso auth login")
        print("\n3. Check database exists:")
        print("   turso db list")
        print("\n4. Check libsql_client is installed:")
        print("   pip install libsql-client")
        return 1

if __name__ == "__main__":
    sys.exit(main())
