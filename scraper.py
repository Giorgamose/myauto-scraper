#!/usr/bin/env python3
"""
Scraper Module - Fetch MyAuto.ge Car Listings
Handles fetching and parsing listings from MyAuto.ge
"""

import requests
import logging
import time
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from parser import MyAutoParser
from urllib.parse import urljoin, quote

logger = logging.getLogger(__name__)


class MyAutoScraper:
    """Scrape car listings from MyAuto.ge"""

    # Real browser user agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scraper with configuration

        Args:
            config: Configuration dict with scraper settings
        """

        self.config = config.get("scraper_settings", {})
        self.base_url = "https://www.myauto.ge/ka"
        self.session = requests.Session()

        # Add session persistence for cookies
        self.session.cookies.clear()

        # Track last request time for delays
        self.last_request_time = 0

        # Setup headers with realistic browser simulation
        self.headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENTS[0]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,ka;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Referer": "https://www.myauto.ge/",
        }

        # Get settings with defaults
        self.timeout = self.config.get("request_timeout_seconds", 15)
        self.delay = self.config.get("delay_between_requests_seconds", 3)
        self.max_retries = self.config.get("max_retries", 5)
        self.retry_delay = self.config.get("retry_delay_seconds", 5)

    def fetch_search_results(self, search_config: Dict[str, Any]) -> List[Dict]:
        """
        Fetch search results from MyAuto.ge

        Args:
            search_config: Search configuration with URL and parameters

        Returns:
            List of listing summaries
        """

        try:
            url = search_config.get("base_url")
            if not url:
                logger.error("[ERROR] No base_url in search config")
                return []

            # Add parameters as query string
            params = search_config.get("parameters", {})

            logger.info(f"[*] Fetching search results: {search_config.get('name')}")
            logger.debug(f"    URL: {url}")

            response = self._make_request(url, params=params)
            if not response:
                return []

            # Parse search results
            listings = self._parse_search_results(response.text, url)

            logger.info(f"[OK] Found {len(listings)} listings in search results")

            return listings

        except Exception as e:
            logger.error(f"[ERROR] Error fetching search results: {e}")
            return []

    def fetch_listing_details(self, listing_id: str) -> Optional[Dict]:
        """
        Fetch complete details for a single listing

        Args:
            listing_id: MyAuto listing ID

        Returns:
            Dict with complete listing details or None
        """

        try:
            url = f"{self.base_url}/pr/{listing_id}"

            logger.debug(f"[*] Fetching listing details: {listing_id}")

            response = self._make_request(url)
            if not response:
                return None

            # Add delay between requests
            time.sleep(self.delay)

            # Parse listing details
            listing_data = self._parse_listing_details(response.text, listing_id, url)

            if listing_data:
                logger.debug(f"[OK] Fetched listing: {listing_id}")
                return listing_data
            else:
                logger.warning(f"[WARN] Could not parse listing: {listing_id}")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Error fetching listing {listing_id}: {e}")
            return None

    def _make_request(self, url: str, params: Dict = None,
                     max_retries: int = None) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic and bot evasion

        Args:
            url: URL to fetch
            params: Query parameters
            max_retries: Override max retries

        Returns:
            Response object or None
        """

        max_retries = max_retries or self.max_retries

        for attempt in range(max_retries):
            try:
                # Enforce delay between requests
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.delay:
                    sleep_time = self.delay - time_since_last
                    logger.debug(f"[*] Enforcing delay: sleeping {sleep_time:.2f}s")
                    time.sleep(sleep_time)

                # Rotate user agent for each attempt
                self.headers["User-Agent"] = self.USER_AGENTS[attempt % len(self.USER_AGENTS)]

                logger.debug(f"[*] Request attempt {attempt + 1}/{max_retries}: {url}")

                response = self.session.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout,
                    allow_redirects=True
                )

                self.last_request_time = time.time()

                response.raise_for_status()

                if response.status_code == 200:
                    logger.debug(f"[OK] Response 200 OK")
                    return response
                else:
                    logger.warning(f"[WARN] HTTP {response.status_code}")

                    # Retry on 403 Forbidden (bot detection) and server errors
                    if response.status_code in [403, 429, 500, 502, 503, 504]:
                        if attempt < max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"[*] Status {response.status_code}: Waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                            continue

                return None

            except requests.exceptions.Timeout:
                logger.warning(f"[WARN] Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None

            except requests.exceptions.ConnectionError:
                logger.warning(f"[WARN] Connection error on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None

            except Exception as e:
                logger.error(f"[ERROR] Error making request: {e}")
                return None

        logger.error(f"[ERROR] Failed after {max_retries} attempts")
        return None

    def _parse_search_results(self, html: str, base_url: str) -> List[Dict]:
        """
        Parse HTML search results and extract listing summaries

        Args:
            html: HTML content
            base_url: Base URL for relative links

        Returns:
            List of listing summaries
        """

        try:
            soup = BeautifulSoup(html, "lxml")

            listings = []

            # Try different selectors for listing cards
            # This may need adjustment based on actual MyAuto.ge structure
            selectors = [
                ".listing-card",  # Common class name
                "div[data-listing-id]",  # Data attribute
                ".car-item",
                "article.listing",
                "div.item"
            ]

            listing_elements = []

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    listing_elements = elements
                    logger.debug(f"[OK] Found {len(elements)} listings using selector: {selector}")
                    break

            # If no specific selectors work, try finding all links to /pr/
            if not listing_elements:
                logger.debug("[*] Using fallback: finding all /pr/ links")

                links = soup.find_all("a", href=lambda x: x and "/pr/" in x)
                listing_elements = [link.find_parent() for link in links if link.find_parent()]

            # Parse each listing
            for element in listing_elements:
                try:
                    listing = MyAutoParser.parse_listing_summary(element)

                    if listing and listing.get("listing_id"):
                        listings.append(listing)

                except Exception as e:
                    logger.debug(f"[WARN] Error parsing listing element: {e}")
                    continue

            return listings

        except Exception as e:
            logger.error(f"[ERROR] Error parsing search results: {e}")
            return []

    def _parse_listing_details(self, html: str, listing_id: str,
                              url: str) -> Optional[Dict]:
        """
        Parse HTML listing detail page and extract all information

        Args:
            html: HTML content
            listing_id: Listing ID
            url: Listing URL

        Returns:
            Dict with complete listing details or None
        """

        try:
            soup = BeautifulSoup(html, "lxml")

            # Start building listing data
            listing_data = {
                "listing_id": listing_id,
                "url": url,
                "vehicle": {},
                "engine": {},
                "condition": {},
                "pricing": {},
                "seller": {},
                "media": {},
                "posted_date": None,
                "last_updated": None
            }

            # Extract main title/heading
            title = MyAutoParser.extract_text(soup, "h1, .title, .listing-title")

            # Extract price
            price_text = MyAutoParser.extract_text(soup, ".price, .listing-price, [data-price]")
            if price_text:
                price_data = MyAutoParser.normalize_price(price_text)
                if price_data:
                    listing_data["pricing"]["price"] = price_data.get("price")
                    listing_data["pricing"]["currency"] = price_data.get("currency")
                    listing_data["pricing"]["currency_id"] = {"USD": 1, "GEL": 2, "EUR": 3}.get(price_data.get("currency"), 1)

            # Extract mileage
            mileage_text = MyAutoParser.extract_text(soup, ".mileage, .km, [data-mileage]")
            if mileage_text:
                listing_data["condition"]["mileage_km"] = MyAutoParser.extract_number(mileage_text)
                listing_data["condition"]["mileage_unit"] = "km"

            # Extract vehicle specs (make, model, year)
            # These selectors may need adjustment based on actual HTML structure
            make = MyAutoParser.extract_text(soup, ".make, [data-make], .brand")
            model = MyAutoParser.extract_text(soup, ".model, [data-model]")
            year_text = MyAutoParser.extract_text(soup, ".year, [data-year]")

            if make:
                listing_data["vehicle"]["make"] = make
            if model:
                listing_data["vehicle"]["model"] = model
            if year_text:
                listing_data["vehicle"]["year"] = MyAutoParser.extract_number(year_text)

            # Extract fuel type
            fuel = MyAutoParser.extract_text(soup, ".fuel-type, [data-fuel]")
            if fuel:
                listing_data["engine"]["fuel_type"] = fuel.capitalize()

            # Extract transmission
            transmission = MyAutoParser.extract_text(soup, ".transmission, [data-transmission]")
            if transmission:
                listing_data["engine"]["transmission"] = transmission.capitalize()

            # Extract location
            location = MyAutoParser.extract_text(soup, ".location, .region, [data-location]")
            if location:
                listing_data["seller"]["location"] = location

            # Extract seller name
            seller_name = MyAutoParser.extract_text(soup, ".seller-name, [data-seller], .seller")
            if seller_name:
                listing_data["seller"]["seller_name"] = seller_name

            # Extract images
            images = []
            img_elements = soup.select("img.listing-photo, img.car-photo, .photo img")

            for img in img_elements[:20]:  # Limit to 20 images
                src = img.get("src") or img.get("data-src")
                if src:
                    # Convert to HTTPS if needed
                    if src.startswith("http"):
                        images.append(src)
                    elif src.startswith("//"):
                        images.append("https:" + src)

            if images:
                listing_data["media"]["photos"] = images
                listing_data["media"]["primary_image_url"] = images[0]
                listing_data["media"]["photo_count"] = len(images)

            # Extract dates (if available)
            # Format: "Posted: 2024-11-09" or similar
            date_text = MyAutoParser.extract_text(soup, ".posted-date, [data-posted], .date")
            if date_text:
                listing_data["posted_date"] = date_text

            listing_data["last_updated"] = __import__("datetime").datetime.now().isoformat()

            # Extract customs cleared status
            customs_text = soup.get_text().lower()
            listing_data["condition"]["customs_cleared"] = "customs" in customs_text and "cleared" in customs_text

            # Extract description
            description = MyAutoParser.extract_text(
                soup,
                ".description, .listing-description, [data-description]"
            )
            if description:
                listing_data["description"] = {
                    "text": description,
                    "features": []
                }

            # Log what we found
            logger.debug(f"[OK] Extracted listing data for {listing_id}")
            logger.debug(f"    Make: {listing_data['vehicle'].get('make')}")
            logger.debug(f"    Model: {listing_data['vehicle'].get('model')}")
            logger.debug(f"    Year: {listing_data['vehicle'].get('year')}")
            logger.debug(f"    Price: {listing_data['pricing'].get('price')}")
            logger.debug(f"    Images: {len(listing_data['media'].get('photos', []))}")

            return listing_data

        except Exception as e:
            logger.error(f"[ERROR] Error parsing listing details: {e}")
            return None

    def close(self):
        """Close session"""

        try:
            self.session.close()
            logger.info("[OK] Session closed")
        except Exception as e:
            logger.error(f"[ERROR] Error closing session: {e}")


def test_scraper():
    """Test scraper (requires network access)"""

    logging.basicConfig(level=logging.INFO)

    logger.info("[*] Testing scraper...")

    # Create minimal config
    config = {
        "scraper_settings": {
            "request_timeout_seconds": 10,
            "delay_between_requests_seconds": 1,
            "user_agent": "Mozilla/5.0",
            "max_retries": 2,
            "retry_delay_seconds": 3
        }
    }

    scraper = MyAutoScraper(config)

    # Try to fetch a single listing
    logger.info("[*] Testing listing fetch...")

    # Use the example listing from the user
    listing_id = "119084515"
    listing = scraper.fetch_listing_details(listing_id)

    if listing:
        logger.info(f"[OK] Successfully fetched listing {listing_id}")
        logger.info(f"    Make: {listing.get('vehicle', {}).get('make')}")
        logger.info(f"    Model: {listing.get('vehicle', {}).get('model')}")
        logger.info(f"    Year: {listing.get('vehicle', {}).get('year')}")
        logger.info(f"    Price: {listing.get('pricing', {}).get('price')}")
        return True
    else:
        logger.warning("[WARN] Could not fetch listing")
        return False


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    try:
        exit(0 if test_scraper() else 1)
    except KeyboardInterrupt:
        logger.info("[*] Interrupted by user")
        sys.exit(0)
