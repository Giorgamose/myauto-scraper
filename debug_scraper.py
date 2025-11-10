#!/usr/bin/env python3
"""
Debug Scraper - Inspect HTML structure for debugging
Helps identify why listings aren't being found
"""

import logging
from dotenv import load_dotenv
from scraper import MyAutoScraper
from bs4 import BeautifulSoup

load_dotenv('.env.local')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test config
test_config = {
    "scraper_settings": {
        "request_timeout_seconds": 20,
        "delay_between_requests_seconds": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "max_retries": 3,
        "retry_delay_seconds": 5
    }
}

search_config = {
    "name": "Toyota Land Cruiser Prado (1995-2008)",
    "base_url": "https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-land-cruiser-prado-1995-2008",
    "parameters": {
        "vehicleType": 0,
        "bargainType": 0,
        "mansNModels": "41.1109.1499",
        "yearFrom": 1995,
        "yearTo": 2008,
        "priceFrom": 11000,
        "priceTo": 18000,
        "currId": 1,
        "mileageType": 1,
        "fuelTypes": 3,
    }
}

def debug_scraper():
    """Debug the scraper to see what HTML is being fetched"""

    print("\n" + "="*70)
    print("  SCRAPER DEBUG - Inspect HTML Structure")
    print("="*70 + "\n")

    scraper = MyAutoScraper(test_config)

    print(f"[*] Fetching: {search_config['base_url']}")
    print(f"[*] Parameters: {search_config.get('parameters', {})}")
    print()

    # Fetch the page
    try:
        response = scraper._make_request(
            search_config['base_url'],
            params=search_config.get('parameters', {})
        )

        if not response:
            print("[ERROR] Failed to fetch page")
            return

        html = response['html']
        print(f"[OK] Fetched HTML: {len(html)} bytes\n")

        # Save HTML to file for inspection
        with open("debug_search_results.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Saved HTML to: debug_search_results.html")

        # Parse and analyze
        soup = BeautifulSoup(html, "lxml")

        print("\n" + "-"*70)
        print("  HTML ANALYSIS")
        print("-"*70 + "\n")

        # Look for common listing containers
        print("[*] Searching for listing containers...")

        selectors_to_test = [
            (".listing-card", "class='listing-card'"),
            ("div[data-listing-id]", "div with data-listing-id"),
            (".car-item", "class='car-item'"),
            ("article.listing", "article with class='listing'"),
            ("div.item", "class='item'"),
            (".product-item", "class='product-item'"),
            ("[data-id]", "elements with data-id"),
            ("a[href*='/pr/']", "links containing /pr/"),
        ]

        for selector, description in selectors_to_test:
            elements = soup.select(selector)
            if elements:
                print(f"  ✓ Found {len(elements)} elements: {description}")
            else:
                print(f"  ✗ No elements found: {description}")

        # Print all links containing /pr/
        print("\n[*] All links containing '/pr/':")
        pr_links = soup.find_all("a", href=lambda x: x and "/pr/" in x)
        if pr_links:
            print(f"  Found {len(pr_links)} listing links:")
            for i, link in enumerate(pr_links[:5]):  # Show first 5
                print(f"    {i+1}. {link.get('href')}")
            if len(pr_links) > 5:
                print(f"    ... and {len(pr_links) - 5} more")
        else:
            print("  ✗ No /pr/ links found!")

        # Check for result messages
        print("\n[*] Checking for result messages:")
        text = soup.get_text()
        if "რეზულტატი" in text or "no results" in text.lower():
            print("  ⚠ Possible 'no results' message found in page")
        else:
            print("  ✓ Page appears to have content")

        # Print page title and main content
        print("\n[*] Page Title:", soup.title.string if soup.title else "No title")

        # Look for total count
        print("\n[*] Searching for result count:")
        count_selectors = [".count", ".total", "[data-count]", "span.count"]
        for selector in count_selectors:
            count_elem = soup.select_one(selector)
            if count_elem:
                print(f"  Found: {selector} = {count_elem.get_text().strip()}")

        # Print first 2000 chars of HTML to see structure
        print("\n[*] First 2000 characters of HTML:")
        print("-"*70)
        print(html[:2000])
        print("-"*70)

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scraper()
