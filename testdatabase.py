import os
from libsql_client import create_client_sync
from libsql_exceptions import LibsqlError

# =============================
# CONFIGURATION
# =============================

# Option 1: Use environment variables (recommended)
DB_URL = os.getenv("TURSO_DATABASE_URL", "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io")
AUTH_TOKEN = os.getenv("eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDIyMkFBQSIsImtpZCI6Imluc18yYzA4R3ZNeEhYMlNCc3l0d2padm95cEdJeDUiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE3NjMyNzg4NzUsImlhdCI6MTc2MjY3NDA3NSwiaXNzIjoiaHR0cHM6Ly9jbGVyay50dXJzby50ZWNoIiwianRpIjoiODhkODQ2NzdkYTI0M2NmNGRkMGMiLCJuYmYiOjE3NjI2NzQwNzAsInN1YiI6InVzZXJfMzVFSzVTRDVuTmZmNVhiQUZESVMxZGdoMm1KIn0.LScVXrlNTMhwEaXb9n-7VzUPY38T8YepMB02fnsy_BqeZxpnF4BeFWCSM816Dq7z2h2Y-3BmoM0oGeYsZggsd0PuVX6UH0o3Q53x8s3V_1ZRTyModRG3Nfk3HkP9nc1JsVP6jOQQ7_FAC92AdkkP7RmkWPgmwc6LokJ5u2ZiFwzJs7VB4jjkT17h8nhU4WYJWp9irOSZDQGW3dl5l2c9K9OhkoEdLWt0m8YH07ZT0QveSE__Kicye1rBKR7r4ltkiOtKjdYH920VoCLB8D8UFiYvxd1mQ6BAfIvK5cH3l84MYxzvX7ZclsJmJNPgnPNyG61aY5u-EyKY1jhgW5-ocg", "")

# Option 2: Hardcode (for quick test)
# DB_URL = "libsql://car-listings-giorgamose.aws-eu-west-1.turso.io"
# AUTH_TOKEN = "your_auth_token_here"

# =============================
# MAIN LOGIC
# =============================

def connect_to_turso(db_url: str, auth_token: str):
    """Creates a synchronous connection to Turso/libSQL."""
    try:
        connection_url = f"{db_url}?authToken={auth_token}"
        client = create_client_sync(connection_url)
        print(f"✅ Connected successfully to {db_url}")
        return client
    except LibsqlError as e:
        print(f"❌ Connection error: {e}")
        exit(1)


def list_tables(client):
    """Returns all tables in the database."""
    try:
        result = client.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in result.rows]
        if tables:
            print("\n📋 Tables found:")
            for t in tables:
                print(f" - {t}")
        else:
            print("⚠️ No tables found in the database.")
        return tables
    except LibsqlError as e:
        print(f"❌ Error listing tables: {e}")
        return []


def show_table_data(client, tables):
    """Prints the first 10 rows of each table."""
    for table in tables:
        print(f"\n📄 Previewing first 10 rows from '{table}':")
        try:
            result = client.execute(f"SELECT * FROM {table} LIMIT 10;")
            if not result.rows:
                print("   (No data)")
                continue

            # Print column names
            print("   Columns:", ", ".join(result.columns))
            for row in result.rows:
                print("   ", dict(zip(result.columns, row)))

        except LibsqlError as e:
            print(f"   ❌ Error reading {table}: {e}")


def main():
    client = connect_to_turso(DB_URL, AUTH_TOKEN)
    tables = list_tables(client)
    if tables:
        show_table_data(client, tables)
    else:
        print("⚠️ No tables found — check schema or data.")
    client.close()
    print("\n✅ Done.")


if __name__ == "__main__":
    main()
