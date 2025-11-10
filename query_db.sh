#!/bin/bash

###############################################################################
# Turso Database Query Script
# Usage: ./query_db.sh [command] [options]
# Examples:
#   ./query_db.sh tables              # Show all tables
#   ./query_db.sh schema              # Show schema info
#   ./query_db.sh stats               # Show database statistics
#   ./query_db.sh listings            # Show all listings
#   ./query_db.sh listings 10          # Show last 10 listings
#   ./query_db.sh listing <id>         # Show specific listing
#   ./query_db.sh notifications       # Show notification logs
#   ./query_db.sh recent              # Show recently added cars
#   ./query_db.sh search               # Show search configurations
###############################################################################

# Load environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '#' | xargs)
elif [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Check if database credentials are set
if [ -z "$TURSO_DATABASE_URL" ] || [ -z "$TURSO_AUTH_TOKEN" ]; then
    echo "ERROR: TURSO_DATABASE_URL and TURSO_AUTH_TOKEN not set"
    echo "Please set these in .env or .env.local file"
    exit 1
fi

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run SQL query
run_query() {
    local query="$1"
    echo -e "${BLUE}[QUERY]${NC} $query"
    turso db shell "$TURSO_DATABASE_URL" --auth-token="$TURSO_AUTH_TOKEN" << EOF
$query
EOF
}

# Function to show all tables
show_tables() {
    echo -e "${GREEN}=== DATABASE TABLES ===${NC}"
    run_query ".tables"
}

# Function to show schema
show_schema() {
    echo -e "${GREEN}=== DATABASE SCHEMA ===${NC}"
    echo ""

    echo -e "${YELLOW}--- seen_listings TABLE ---${NC}"
    run_query ".schema seen_listings"
    echo ""

    echo -e "${YELLOW}--- vehicle_details TABLE ---${NC}"
    run_query ".schema vehicle_details"
    echo ""

    echo -e "${YELLOW}--- search_configurations TABLE ---${NC}"
    run_query ".schema search_configurations"
    echo ""

    echo -e "${YELLOW}--- notifications_sent TABLE ---${NC}"
    run_query ".schema notifications_sent"
}

# Function to show database statistics
show_stats() {
    echo -e "${GREEN}=== DATABASE STATISTICS ===${NC}"
    echo ""

    echo -e "${YELLOW}Total Listings:${NC}"
    run_query "SELECT COUNT(*) as count FROM seen_listings;"
    echo ""

    echo -e "${YELLOW}Listings from Last 24 Hours:${NC}"
    run_query "SELECT COUNT(*) as count FROM seen_listings WHERE created_at > datetime('now', '-1 day');"
    echo ""

    echo -e "${YELLOW}Notifications Sent (Last 24 Hours):${NC}"
    run_query "SELECT COUNT(*) as count FROM notifications_sent WHERE sent_at > datetime('now', '-1 day') AND success = 1;"
    echo ""

    echo -e "${YELLOW}Total Vehicles in Database:${NC}"
    run_query "SELECT COUNT(*) as count FROM vehicle_details;"
    echo ""

    echo -e "${YELLOW}Search Configurations:${NC}"
    run_query "SELECT COUNT(*) as count FROM search_configurations;"
}

# Function to show all listings
show_listings() {
    local limit=${1:-20}
    echo -e "${GREEN}=== LATEST LISTINGS (Last $limit) ===${NC}"
    echo ""
    run_query "SELECT id, created_at, notified FROM seen_listings ORDER BY created_at DESC LIMIT $limit;"
}

# Function to show specific listing details
show_listing() {
    local listing_id=$1

    if [ -z "$listing_id" ]; then
        echo -e "${RED}ERROR: Please provide listing ID${NC}"
        echo "Usage: ./query_db.sh listing <listing_id>"
        exit 1
    fi

    echo -e "${GREEN}=== LISTING DETAILS: $listing_id ===${NC}"
    echo ""

    echo -e "${YELLOW}--- Listing Summary ---${NC}"
    run_query "SELECT * FROM seen_listings WHERE id = '$listing_id';"
    echo ""

    echo -e "${YELLOW}--- Vehicle Details ---${NC}"
    run_query "SELECT listing_id, make, model, year, price, currency, mileage_km, location, seller_name FROM vehicle_details WHERE listing_id = '$listing_id';"
}

# Function to show notification logs
show_notifications() {
    local limit=${1:-20}
    echo -e "${GREEN}=== NOTIFICATION LOGS (Last $limit) ===${NC}"
    echo ""
    run_query "SELECT id, listing_id, notification_type, sent_at, success FROM notifications_sent ORDER BY sent_at DESC LIMIT $limit;"
}

# Function to show recently added cars
show_recent() {
    local days=${1:-7}
    echo -e "${GREEN}=== RECENTLY ADDED CARS (Last $days days) ===${NC}"
    echo ""
    run_query "SELECT s.id, s.created_at, v.make, v.model, v.year, v.price, v.currency, v.location FROM seen_listings s LEFT JOIN vehicle_details v ON s.id = v.listing_id WHERE s.created_at > datetime('now', '-$days days') ORDER BY s.created_at DESC;"
}

# Function to show cars by make
show_cars_by_make() {
    echo -e "${GREEN}=== CARS BY MAKE ===${NC}"
    echo ""
    run_query "SELECT make, COUNT(*) as count FROM vehicle_details GROUP BY make ORDER BY count DESC;"
}

# Function to show cars by price range
show_cars_by_price() {
    echo -e "${GREEN}=== CARS BY PRICE RANGE ===${NC}"
    echo ""
    run_query "SELECT
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
    GROUP BY price_range;"
}

# Function to show search configurations
show_searches() {
    echo -e "${GREEN}=== SEARCH CONFIGURATIONS ===${NC}"
    echo ""
    run_query "SELECT id, name, vehicle_make, vehicle_model, price_from, price_to, is_active, last_checked_at FROM search_configurations;"
}

# Function to export listings to CSV
export_listings() {
    local filename=${1:-listings_export.csv}
    echo -e "${GREEN}=== EXPORTING LISTINGS TO CSV ===${NC}"
    echo "Exporting to: $filename"
    echo ""
    run_query ".mode csv
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
ORDER BY s.created_at DESC;" > "$filename"
    echo -e "${GREEN}✓ Export complete: $filename${NC}"
}

# Function to show help
show_help() {
    cat << EOF
${GREEN}=== Turso Database Query Script ===${NC}

${YELLOW}Usage:${NC} ./query_db.sh [command] [options]

${YELLOW}Commands:${NC}

  ${BLUE}tables${NC}                    Show all database tables
  ${BLUE}schema${NC}                    Show database schema
  ${BLUE}stats${NC}                     Show database statistics
  ${BLUE}listings${NC} [limit]          Show all listings (default: 20)
  ${BLUE}listing${NC} <id>              Show details for specific listing
  ${BLUE}notifications${NC} [limit]     Show notification logs (default: 20)
  ${BLUE}recent${NC} [days]             Show cars added in last N days (default: 7)
  ${BLUE}by-make${NC}                   Show car count by make
  ${BLUE}by-price${NC}                  Show car count by price range
  ${BLUE}search${NC}                    Show search configurations
  ${BLUE}export${NC} [filename]         Export all listings to CSV
  ${BLUE}help${NC}                      Show this help message

${YELLOW}Examples:${NC}

  ./query_db.sh tables
  ./query_db.sh stats
  ./query_db.sh listings 50
  ./query_db.sh listing 119084515
  ./query_db.sh recent 30
  ./query_db.sh by-make
  ./query_db.sh export my_listings.csv

${YELLOW}Environment Variables:${NC}

  TURSO_DATABASE_URL      - Your Turso database URL
  TURSO_AUTH_TOKEN        - Your Turso authentication token

  Set these in .env or .env.local file

${YELLOW}Requirements:${NC}

  - Turso CLI installed (https://docs.turso.tech/reference/turso-cli)
  - Database credentials in .env or .env.local

EOF
}

# Main script logic
case "${1:-help}" in
    tables)
        show_tables
        ;;
    schema)
        show_schema
        ;;
    stats)
        show_stats
        ;;
    listings)
        show_listings "${2:-20}"
        ;;
    listing)
        show_listing "$2"
        ;;
    notifications)
        show_notifications "${2:-20}"
        ;;
    recent)
        show_recent "${2:-7}"
        ;;
    by-make)
        show_cars_by_make
        ;;
    by-price)
        show_cars_by_price
        ;;
    search)
        show_searches
        ;;
    export)
        export_listings "${2:-listings_export.csv}"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
