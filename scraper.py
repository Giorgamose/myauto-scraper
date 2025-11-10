#!/usr/bin/env python3
"""
Scraper Module - Fetch MyAuto.ge Car Listings
Handles fetching and parsing listings from MyAuto.ge
Uses Playwright for JavaScript-enabled scraping to bypass bot detection
"""

import logging
import time
import random
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from parser import MyAutoParser
from urllib.parse import urljoin, quote, urlencode

try:
    from playwright.sync_api import sync_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Page = None

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

        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("[WARN] Playwright not installed. Install with: pip install playwright")

        self.config = config.get("scraper_settings", {})
        self.base_url = "https://www.myauto.ge/ka"

        # Playwright resources (initialized on first use)
        self.playwright = None
        self.browser = None
        self.context = None

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
        self.timeout = self.config.get("request_timeout_seconds", 15) * 1000  # Convert to ms for Playwright
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
            listings = self._parse_search_results(response["html"], url)

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
            listing_data = self._parse_listing_details(response["html"], listing_id, url)

            if listing_data:
                logger.debug(f"[OK] Fetched listing: {listing_id}")
                return listing_data
            else:
                logger.warning(f"[WARN] Could not parse listing: {listing_id}")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Error fetching listing {listing_id}: {e}")
            return None

    def _init_browser(self):
        """Initialize Playwright browser context"""
        if self.browser is not None:
            return

        try:
            logger.debug("[*] Initializing Playwright browser...")
            self.playwright = sync_playwright().start()

            # Launch browser with stealth settings to avoid detection
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )

            # Create context with realistic viewport and user agent
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=self.headers.get("User-Agent", self.USER_AGENTS[0]),
                extra_http_headers={
                    "Accept-Language": self.headers["Accept-Language"],
                    "Accept": self.headers["Accept"],
                    "Referer": self.headers["Referer"],
                },
                ignore_https_errors=True,  # Ignore SSL issues
            )

            logger.debug("[OK] Playwright browser initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Playwright: {e}")
            raise

    def _make_request(self, url: str, params: Dict = None,
                     max_retries: int = None) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with retry logic and bot evasion using Playwright

        Args:
            url: URL to fetch
            params: Query parameters
            max_retries: Override max retries

        Returns:
            Dict with 'html' and 'status' keys, or None on failure
        """

        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[ERROR] Playwright not installed. Install with: pip install playwright")
            return None

        max_retries = max_retries or self.max_retries

        # Initialize browser on first use
        if self.browser is None:
            self._init_browser()

        for attempt in range(max_retries):
            try:
                # Enforce delay between requests
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.delay:
                    sleep_time = self.delay - time_since_last
                    logger.debug(f"[*] Enforcing delay: sleeping {sleep_time:.2f}s")
                    time.sleep(sleep_time)

                # Add random jitter to seem more human-like
                jitter = random.uniform(0.1, 0.5)
                time.sleep(jitter)

                # Build full URL with parameters
                full_url = url
                if params:
                    full_url = f"{url}?{urlencode(params)}"

                logger.info(f"[*] Request attempt {attempt + 1}/{max_retries}")
                logger.debug(f"    URL: {full_url}")
                logger.debug(f"    Timeout: {self.timeout}ms")
                logger.debug(f"    Browser: Chromium (headless)")

                # Create a new page for this request (better isolation)
                page = self.context.new_page()

                try:
                    # Navigate to URL with Playwright (executes JavaScript)
                    # Headers are inherited from context
                    logger.debug(f"[*] Navigating with Playwright...")
                    response = page.goto(
                        full_url,
                        wait_until="load",
                        timeout=self.timeout
                    )

                    self.last_request_time = time.time()

                    if response is None:
                        logger.warning(f"[WARN] No response object returned on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"[*] Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        return None

                    status_code = response.status

                    # Wait for content to load (for React/dynamic apps)
                    # Try to wait for listing elements to appear
                    logger.debug("[*] Waiting for content to render...")
                    try:
                        # Wait for either search results or "no results" message
                        page.wait_for_selector(
                            'a[href*="/pr/"], [class*="no-result"], [class*="empty"]',
                            timeout=5000
                        )
                        logger.debug("[OK] Content loaded")
                    except Exception as e:
                        logger.debug(f"[*] Content wait timed out or failed (may be OK): {e}")
                        # Continue anyway - page might still have content

                    # Add a small delay to ensure content is fully rendered
                    time.sleep(2)

                    html_content = page.content()

                    # Log response details
                    logger.info(f"[RESPONSE] Status: {status_code}")
                    logger.debug(f"    HTML size: {len(html_content)} bytes")

                    # Log response headers
                    try:
                        headers = response.headers
                        logger.debug(f"    Response headers:")
                        for key, value in headers.items():
                            logger.debug(f"      {key}: {value}")
                    except Exception as e:
                        logger.debug(f"    Could not read headers: {e}")

                    # Log first 300 chars of HTML for inspection
                    html_snippet = html_content[:300].replace('\n', ' ').replace('\t', ' ')
                    logger.debug(f"    HTML snippet: {html_snippet}...")

                    # Check status code
                    if status_code == 200:
                        logger.info(f"[OK] Response 200 OK - Request successful")
                        return {"html": html_content, "status": status_code}

                    # Handle retryable error codes (403, 429, 5xx)
                    if status_code in [403, 429, 500, 502, 503, 504]:
                        logger.warning(f"[WARN] Received status {status_code} - retryable error")

                        # Log error page content for debugging
                        if status_code == 403:
                            logger.warning(f"[WARN] 403 Forbidden - possible bot detection")
                            error_snippet = html_content[:200].replace('\n', ' ')
                            logger.debug(f"    Error page snippet: {error_snippet}...")

                        if attempt < max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"[*] Retry {attempt + 2}/{max_retries} in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"[ERROR] Max retries exceeded for status {status_code}")
                            return None

                    # For other non-200 codes, log error
                    logger.warning(f"[WARN] Unexpected status {status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None

                finally:
                    page.close()

            except Exception as e:
                logger.warning(f"[WARN] Error on attempt {attempt + 1}: {type(e).__name__}: {e}")
                import traceback
                logger.debug(f"    Traceback: {traceback.format_exc()}")
                if attempt < max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"[*] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return None

        logger.error(f"[ERROR] Failed after {max_retries} attempts - giving up")
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
        """Close Playwright browser"""

        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("[OK] Playwright browser closed")
        except Exception as e:
            logger.error(f"[ERROR] Error closing browser: {e}")


def test_scraper():
    """Test scraper (requires network access and Playwright)"""

    logging.basicConfig(level=logging.INFO)

    logger.info("[*] Testing scraper with Playwright...")

    if not PLAYWRIGHT_AVAILABLE:
        logger.error("[ERROR] Playwright not available. Install with: pip install playwright")
        return False

    # Create minimal config
    config = {
        "scraper_settings": {
            "request_timeout_seconds": 30,
            "delay_between_requests_seconds": 2,
            "user_agent": "Mozilla/5.0",
            "max_retries": 2,
            "retry_delay_seconds": 5
        }
    }

    scraper = MyAutoScraper(config)

    try:
        # Try to fetch a simple search first (faster test)
        logger.info("[*] Testing search fetch...")
        response = scraper._make_request("https://www.myauto.ge/ka/s/iyideba-manqanebi")

        if response:
            logger.info(f"[OK] Successfully fetched search page (status {response['status']})")
            logger.info(f"    HTML size: {len(response['html'])} bytes")
            return True
        else:
            logger.warning("[WARN] Could not fetch search page")
            return False

    finally:
        scraper.close()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    try:
        exit(0 if test_scraper() else 1)
    except KeyboardInterrupt:
        logger.info("[*] Interrupted by user")
        sys.exit(0)
