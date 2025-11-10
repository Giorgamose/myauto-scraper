#!/usr/bin/env python3
"""
Supabase Database Query Tool
Query and inspect your Supabase database via command line

Usage:
    python query_db.py stats            # Show statistics
    python query_db.py listings [limit] # Show recent listings
    python query_db.py listing <id>     # Show specific listing details
"""

import os
import sys
import logging
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
from database_rest_api import DatabaseManager


class Colors:
    """ANSI color codes for terminal output"""
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
    try:
        db = DatabaseManager()
        if db.connection_failed:
            print(f"{Colors.RED}ERROR: Failed to connect to Supabase{Colors.ENDC}")
            print("Please set SUPABASE_URL and SUPABASE_API_KEY in .env or .env.local")
            sys.exit(1)
        return db
    except Exception as e:
        print(f"{Colors.RED}ERROR: Failed to connect to database: {e}{Colors.ENDC}")
        sys.exit(1)


def print_header(title):
    """Print formatted header"""
    print(f"\n{Colors.GREEN}{'='*60}")
    print(f"{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{'='*60}{Colors.ENDC}\n")


def show_stats():
    """Show database statistics"""
    db = get_db()
    print_header("DATABASE STATISTICS")

    try:
        stats = db.get_statistics()

        print(f"{Colors.CYAN}Total Listings:{Colors.ENDC} {stats.get('total_listings', 'N/A')}")
        print(f"{Colors.CYAN}Recent Listings (24h):{Colors.ENDC} {stats.get('recent_listings_24h', 'N/A')}")
        print(f"{Colors.CYAN}Last Updated:{Colors.ENDC} {stats.get('last_updated', 'N/A')}")

    except Exception as e:
        print(f"{Colors.RED}Error retrieving statistics: {e}{Colors.ENDC}")


def show_listings(limit=20):
    """Show recent listings"""
    db = get_db()
    print_header(f"RECENT LISTINGS (Last {limit})")

    try:
        # Fetch listings using REST API
        import requests

        response = requests.get(
            f"{db.base_url}/seen_listings?order=created_at.desc&limit={limit}&select=id,created_at,notified",
            headers=db.headers,
            timeout=10
        )

        if response.status_code != 200:
            print(f"{Colors.RED}Error: {response.status_code} - {response.text}{Colors.ENDC}")
            return

        listings = response.json()

        if not listings:
            print(f"{Colors.YELLOW}No listings found{Colors.ENDC}")
            return

        for listing in listings:
            print(f"{Colors.CYAN}ID:{Colors.ENDC} {listing.get('id')}")
            print(f"  {Colors.YELLOW}Created:{Colors.ENDC} {listing.get('created_at')}")
            print(f"  {Colors.YELLOW}Notified:{Colors.ENDC} {listing.get('notified')}")
            print()

        print(f"{Colors.GREEN}Total: {len(listings)} listings{Colors.ENDC}")

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
        import requests

        # Get listing summary
        print(f"{Colors.YELLOW}--- Listing Summary ---{Colors.ENDC}")
        response = requests.get(
            f"{db.base_url}/seen_listings?id=eq.{listing_id}",
            headers=db.headers,
            timeout=10
        )

        if response.status_code != 200:
            print(f"{Colors.RED}Error: {response.status_code}{Colors.ENDC}")
            return

        listings = response.json()
        if listings:
            listing = listings[0]
            print(f"{Colors.CYAN}ID:{Colors.ENDC} {listing.get('id')}")
            print(f"{Colors.CYAN}Created:{Colors.ENDC} {listing.get('created_at')}")
            print(f"{Colors.CYAN}Notified:{Colors.ENDC} {listing.get('notified')}")
        else:
            print(f"{Colors.RED}No listing found with ID: {listing_id}{Colors.ENDC}")

        # Get vehicle details
        print(f"\n{Colors.YELLOW}--- Vehicle Details ---{Colors.ENDC}")
        response = requests.get(
            f"{db.base_url}/vehicle_details?listing_id=eq.{listing_id}",
            headers=db.headers,
            timeout=10
        )

        if response.status_code == 200:
            vehicles = response.json()
            if vehicles:
                vehicle = vehicles[0]
                print(f"{Colors.CYAN}Make:{Colors.ENDC} {vehicle.get('make')}")
                print(f"{Colors.CYAN}Model:{Colors.ENDC} {vehicle.get('model')}")
                print(f"{Colors.CYAN}Year:{Colors.ENDC} {vehicle.get('year')}")
                print(f"{Colors.CYAN}Price:{Colors.ENDC} {vehicle.get('price')} {vehicle.get('currency')}")
                print(f"{Colors.CYAN}Mileage:{Colors.ENDC} {vehicle.get('mileage_km')} km")
                print(f"{Colors.CYAN}Location:{Colors.ENDC} {vehicle.get('location')}")
                print(f"{Colors.CYAN}Seller:{Colors.ENDC} {vehicle.get('seller_name')}")
                print(f"{Colors.CYAN}URL:{Colors.ENDC} {vehicle.get('url')}")
            else:
                print(f"{Colors.YELLOW}No vehicle details found{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Error retrieving vehicle details: {response.status_code}{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}Error retrieving listing: {e}{Colors.ENDC}")


def show_help():
    """Show help message"""
    print(f"""
{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}
{Colors.GREEN}║     Supabase Database Query Tool - Help{Colors.ENDC}
{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.YELLOW}Usage:{Colors.ENDC}
    python query_db.py [command] [options]

{Colors.YELLOW}Commands:{Colors.ENDC}

    {Colors.CYAN}stats{Colors.ENDC}                     Show database statistics
    {Colors.CYAN}listings{Colors.ENDC} [limit]          Show recent listings (default: 20)
    {Colors.CYAN}listing{Colors.ENDC} <id>              Show details for specific listing
    {Colors.CYAN}help{Colors.ENDC}                      Show this help message

{Colors.YELLOW}Examples:{Colors.ENDC}

    python query_db.py stats
    python query_db.py listings
    python query_db.py listings 50
    python query_db.py listing 119084515

{Colors.YELLOW}Environment Variables:{Colors.ENDC}

    SUPABASE_URL       Your Supabase project URL
    SUPABASE_API_KEY   Your Supabase API key

    Set these in .env or .env.local file

{Colors.ENDC}
""")


def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if command == "stats":
        show_stats()
    elif command == "listings":
        limit = int(args[0]) if args else 20
        show_listings(limit)
    elif command == "listing":
        if not args:
            print(f"{Colors.RED}ERROR: Please provide listing ID{Colors.ENDC}")
            sys.exit(1)
        show_listing(args[0])
    elif command in ["help", "--help", "-h"]:
        show_help()
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.ENDC}")
        print(f"Run {Colors.CYAN}python query_db.py help{Colors.ENDC} for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
