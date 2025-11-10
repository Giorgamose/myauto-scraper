#!/usr/bin/env python3
"""
Turso Database Query Tool
Query and inspect your database via command line

Usage:
    python query_db.py tables           # Show all tables
    python query_db.py schema           # Show database schema
    python query_db.py stats            # Show statistics
    python query_db.py listings [limit] # Show listings
    python query_db.py listing <id>     # Show specific listing
    python query_db.py notifications    # Show notification logs
    python query_db.py recent [days]    # Show recent cars
    python query_db.py by-make          # Group by make
    python query_db.py by-price         # Group by price range
    python query_db.py search           # Show searches
    python query_db.py export [file]    # Export to CSV
"""

import os
import sys
import logging
from tabulate import tabulate
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database manager
sys.path.insert(0, str(Path(__file__).parent))
from database import DatabaseManager

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_db():
    """Initialize database connection"""
    db_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not db_url or not auth_token:
        print(f"{Colors.RED}ERROR: Database credentials not found{Colors.ENDC}")
        print("Please set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env or .env.local")
        sys.exit(1)

    try:
        db = DatabaseManager(db_url, auth_token)
        return db
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to connect to database: {e}{Colors.ENDC}")
        sys.exit(1)

def print_header(title):
    """Print formatted header"""
    print(f"\n{Colors.GREEN}{'='*60}")
    print(f"{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{'='*60}{Colors.ENDC}\n")

def show_tables():
    """Show all tables"""
    db = get_db()
    print_header("DATABASE TABLES")

    result = db.client.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in result]

    for table in tables:
        print(f"  • {Colors.CYAN}{table}{Colors.ENDC}")

def show_schema():
    """Show database schema"""
    db = get_db()
    print_header("DATABASE SCHEMA")

    tables = ["seen_listings", "vehicle_details", "search_configurations", "notifications_sent"]

    for table in tables:
        try:
            print(f"\n{Colors.YELLOW}--- {table} TABLE ---{Colors.ENDC}")
            result = db.client.execute(f"PRAGMA table_info({table});")

            headers = ["Column", "Type", "Not Null", "Default", "PK"]
            rows = []
            for row in result:
                rows.append([row[1], row[2], "Yes" if row[3] else "No", row[4], row[5]])

            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"{Colors.RED}Error reading {table}: {e}{Colors.ENDC}")

def show_stats():
    """Show database statistics"""
    db = get_db()
    print_header("DATABASE STATISTICS")

    try:
        stats = db.get_statistics()

        data = [
            ["Total Listings", stats.get("total_listings", 0)],
            ["Recent Listings (24h)", stats.get("recent_listings_24h", 0)],
            ["Notifications Sent (24h)", stats.get("notifications_sent_24h", 0)],
        ]

        # Count vehicles
        vehicle_count = db.client.execute("SELECT COUNT(*) FROM vehicle_details;")
        vehicles = vehicle_count[0][0] if vehicle_count else 0
        data.append(["Vehicles in Database", vehicles])

        # Count searches
        search_count = db.client.execute("SELECT COUNT(*) FROM search_configurations;")
        searches = search_count[0][0] if search_count else 0
        data.append(["Search Configurations", searches])

        print(tabulate(data, headers=["Metric", "Count"], tablefmt="grid"))

    except Exception as e:
        print(f"{Colors.RED}Error retrieving statistics: {e}{Colors.ENDC}")

def show_listings(limit=20):
    """Show listings"""
    db = get_db()
    print_header(f"LATEST LISTINGS (Last {limit})")

    try:
        result = db.client.execute(
            f"SELECT id, created_at, notified FROM seen_listings ORDER BY created_at DESC LIMIT {limit};"
        )

        headers = ["Listing ID", "Created At", "Notified"]
        print(tabulate(result, headers=headers, tablefmt="grid"))
        print(f"\n{Colors.GREEN}Total: {len(result)} listings{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}Error retrieving listings: {e}{Colors.ENDC}")

def show_listing(listing_id):
    """Show specific listing details"""
    if not listing_id:
        print(f"{Colors.RED}ERROR: Please provide listing ID{Colors.ENDC}")
        sys.exit(1)

    db = get_db()
    print_header(f"LISTING DETAILS: {listing_id}")

    try:
        # Get listing summary
        print(f"{Colors.YELLOW}--- Listing Summary ---{Colors.ENDC}")
        result = db.client.execute(
            f"SELECT id, created_at, notified FROM seen_listings WHERE id = '{listing_id}';"
        )
        if result:
            headers = ["ID", "Created At", "Notified"]
            print(tabulate(result, headers=headers, tablefmt="grid"))
        else:
            print(f"No listing found with ID: {listing_id}")

        # Get vehicle details
        print(f"\n{Colors.YELLOW}--- Vehicle Details ---{Colors.ENDC}")
        result = db.client.execute(
            f"""SELECT listing_id, make, model, year, price, currency, mileage_km, location, seller_name
               FROM vehicle_details WHERE listing_id = '{listing_id}';"""
        )
        if result:
            headers = ["ID", "Make", "Model", "Year", "Price", "Currency", "Mileage (km)", "Location", "Seller"]
            print(tabulate(result, headers=headers, tablefmt="grid"))
        else:
            print("No vehicle details found")

    except Exception as e:
        print(f"{Colors.RED}Error retrieving listing: {e}{Colors.ENDC}")

def show_notifications(limit=20):
    """Show notification logs"""
    db = get_db()
    print_header(f"NOTIFICATION LOGS (Last {limit})")

    try:
        result = db.client.execute(
            f"SELECT id, listing_id, notification_type, sent_at, success FROM notifications_sent ORDER BY sent_at DESC LIMIT {limit};"
        )

        headers = ["ID", "Listing ID", "Type", "Sent At", "Success"]
        print(tabulate(result, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"{Colors.RED}Error retrieving notifications: {e}{Colors.ENDC}")

def show_recent(days=7):
    """Show recently added cars"""
    db = get_db()
    print_header(f"RECENTLY ADDED CARS (Last {days} days)")

    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        result = db.client.execute(
            f"""SELECT s.id, s.created_at, v.make, v.model, v.year, v.price, v.currency, v.location
               FROM seen_listings s
               LEFT JOIN vehicle_details v ON s.id = v.listing_id
               WHERE s.created_at > '{cutoff}'
               ORDER BY s.created_at DESC;"""
        )

        headers = ["ID", "Created", "Make", "Model", "Year", "Price", "Currency", "Location"]
        print(tabulate(result, headers=headers, tablefmt="grid"))
        print(f"\n{Colors.GREEN}Total: {len(result)} cars added in last {days} days{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}Error retrieving recent listings: {e}{Colors.ENDC}")

def show_cars_by_make():
    """Show cars grouped by make"""
    db = get_db()
    print_header("CARS BY MAKE")

    try:
        result = db.client.execute(
            "SELECT make, COUNT(*) as count FROM vehicle_details WHERE make IS NOT NULL GROUP BY make ORDER BY count DESC;"
        )

        headers = ["Make", "Count"]
        print(tabulate(result, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"{Colors.RED}Error retrieving data: {e}{Colors.ENDC}")

def show_cars_by_price():
    """Show cars grouped by price range"""
    db = get_db()
    print_header("CARS BY PRICE RANGE")

    try:
        result = db.client.execute("""
            SELECT
                CASE
                    WHEN price < 5000 THEN 'Under 5K'
                    WHEN price < 10000 THEN '5K-10K'
                    WHEN price < 20000 THEN '10K-20K'
                    WHEN price < 50000 THEN '20K-50K'
                    ELSE 'Over 50K'
                END as price_range,
                COUNT(*) as count
            FROM vehicle_details
            WHERE price IS NOT NULL
            GROUP BY price_range
            ORDER BY count DESC;
        """)

        headers = ["Price Range", "Count"]
        print(tabulate(result, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"{Colors.RED}Error retrieving data: {e}{Colors.ENDC}")

def show_searches():
    """Show search configurations"""
    db = get_db()
    print_header("SEARCH CONFIGURATIONS")

    try:
        result = db.client.execute(
            "SELECT id, name, vehicle_make, vehicle_model, price_from, price_to, is_active FROM search_configurations;"
        )

        headers = ["ID", "Name", "Make", "Model", "Price From", "Price To", "Active"]
        print(tabulate(result, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"{Colors.RED}Error retrieving searches: {e}{Colors.ENDC}")

def export_listings(filename="listings_export.csv"):
    """Export listings to CSV"""
    db = get_db()
    print_header(f"EXPORTING LISTINGS TO {filename}")

    try:
        result = db.client.execute("""
            SELECT
                s.id,
                s.created_at,
                s.notified,
                v.make,
                v.model,
                v.year,
                v.price,
                v.currency,
                v.mileage_km,
                v.location,
                v.seller_name,
                v.url
            FROM seen_listings s
            LEFT JOIN vehicle_details v ON s.id = v.listing_id
            ORDER BY s.created_at DESC;
        """)

        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Created At", "Notified", "Make", "Model", "Year", "Price", "Currency", "Mileage", "Location", "Seller", "URL"])
            writer.writerows(result)

        print(f"{Colors.GREEN}✓ Export complete: {filename}{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Total records exported: {len(result)}{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}Error exporting: {e}{Colors.ENDC}")

def show_help():
    """Show help message"""
    print(f"""
{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}
{Colors.GREEN}║     Turso Database Query Tool - Help{Colors.ENDC}
{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.YELLOW}Usage:{Colors.ENDC}
    python query_db.py [command] [options]

{Colors.YELLOW}Commands:{Colors.ENDC}

    {Colors.CYAN}tables{Colors.ENDC}                    Show all database tables
    {Colors.CYAN}schema{Colors.ENDC}                    Show database schema with column info
    {Colors.CYAN}stats{Colors.ENDC}                     Show database statistics
    {Colors.CYAN}listings{Colors.ENDC} [limit]          Show all listings (default: 20)
    {Colors.CYAN}listing{Colors.ENDC} <id>              Show details for specific listing
    {Colors.CYAN}notifications{Colors.ENDC} [limit]     Show notification logs (default: 20)
    {Colors.CYAN}recent{Colors.ENDC} [days]             Show cars added in last N days (default: 7)
    {Colors.CYAN}by-make{Colors.ENDC}                   Show car count by make (manufacturer)
    {Colors.CYAN}by-price{Colors.ENDC}                  Show car count by price range
    {Colors.CYAN}search{Colors.ENDC}                    Show search configurations
    {Colors.CYAN}export{Colors.ENDC} [filename]         Export all listings to CSV file
    {Colors.CYAN}help{Colors.ENDC}                      Show this help message

{Colors.YELLOW}Examples:{Colors.ENDC}

    python query_db.py tables
    python query_db.py stats
    python query_db.py listings 50
    python query_db.py listing 119084515
    python query_db.py recent 30
    python query_db.py by-make
    python query_db.py by-price
    python query_db.py export my_listings.csv

{Colors.YELLOW}Environment Variables:{Colors.ENDC}

    TURSO_DATABASE_URL     Your Turso database URL
    TURSO_AUTH_TOKEN       Your Turso authentication token

    Set these in .env or .env.local file

{Colors.YELLOW}Requirements:{Colors.ENDC}

    pip install tabulate python-dotenv libsql-client

{Colors.ENDC}
""")

def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if command == "tables":
        show_tables()
    elif command == "schema":
        show_schema()
    elif command == "stats":
        show_stats()
    elif command == "listings":
        limit = int(args[0]) if args else 20
        show_listings(limit)
    elif command == "listing":
        if not args:
            print(f"{Colors.RED}ERROR: Please provide listing ID{Colors.ENDC}")
            sys.exit(1)
        show_listing(args[0])
    elif command == "notifications":
        limit = int(args[0]) if args else 20
        show_notifications(limit)
    elif command == "recent":
        days = int(args[0]) if args else 7
        show_recent(days)
    elif command == "by-make":
        show_cars_by_make()
    elif command == "by-price":
        show_cars_by_price()
    elif command == "search":
        show_searches()
    elif command == "export":
        filename = args[0] if args else "listings_export.csv"
        export_listings(filename)
    elif command in ["help", "--help", "-h"]:
        show_help()
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.ENDC}")
        print(f"Run {Colors.CYAN}python query_db.py help{Colors.ENDC} for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main()
