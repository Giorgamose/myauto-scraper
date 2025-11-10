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
                    logger.debug("[*] Waiting for content to render...")

                    # Check if this is a detail page (/pr/) or search results page
                    is_detail_page = "/pr/" in full_url

                    try:
                        if is_detail_page:
                            # For detail pages, wait for vehicle-specific elements
                            logger.debug("[*] Detail page detected - waiting for vehicle info...")
                            page.wait_for_selector(
                                'h1, [class*="price"], [class*="make"], [class*="model"], [class*="year"], [class*="mileage"]',
                                timeout=6000
                            )
                            logger.debug("[OK] Vehicle info elements loaded")
                        else:
                            # For search results, wait for listing links or "no results"
                            logger.debug("[*] Search results page - waiting for listings...")
                            page.wait_for_selector(
                                'a[href*="/pr/"], [class*="no-result"], [class*="empty"]',
                                timeout=5000
                            )
                            logger.debug("[OK] Listings loaded")
                    except Exception as e:
                        logger.debug(f"[*] Content wait timed out or failed (may be OK): {e}")
                        # Continue anyway - page might still have content

                    # Add delay to ensure content is fully rendered
                    # Detail pages may need more time for React rendering
                    delay = 3 if is_detail_page else 2
                    time.sleep(delay)

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
                # Walk up to find the actual listing card container
                # Link structure: <a> → <div> → <div class="flex flex-col..."> (listing card)
                listing_elements = []
                seen_elements = set()  # Track already-added containers to avoid duplicates

                for link in links:
                    # Start from the link and walk up to find the listing container
                    current = link
                    for _ in range(5):  # Walk up max 5 levels
                        if current:
                            current = current.parent
                            if current and current.name == "div":
                                # Check if this div has multiple children (likely the container)
                                children = [c for c in current.children if hasattr(c, 'name')]
                                if len(children) >= 3:
                                    # Use object id to avoid duplicate containers
                                    elem_id = id(current)
                                    if elem_id not in seen_elements:
                                        listing_elements.append(current)
                                        seen_elements.add(elem_id)
                                    break

            # Parse each listing and deduplicate by ID
            seen_ids = set()
            for element in listing_elements:
                try:
                    listing = MyAutoParser.parse_listing_summary(element)

                    if listing and listing.get("listing_id"):
                        listing_id = listing.get("listing_id")
                        # Avoid adding duplicate listings
                        if listing_id not in seen_ids:
                            listings.append(listing)
                            seen_ids.add(listing_id)

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
        Tries multiple extraction strategies for React SPA content

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

            # STRATEGY 1: Try to extract vehicle info from heading
            logger.debug("[*] Attempting heading extraction...")
            heading_data = MyAutoParser.extract_vehicle_from_heading(soup)

            if heading_data:
                logger.debug("[OK] Found vehicle data in heading")
                listing_data["vehicle"].update(heading_data)

            # STRATEGY 1B: Extract Georgian-labeled fields (comprehensive field extraction)
            logger.debug("[*] Attempting Georgian labeled field extraction...")
            georgian_data = MyAutoParser.extract_georgian_labeled_fields(soup)

            if georgian_data:
                logger.debug("[OK] Found Georgian labeled fields")
                # Distribute fields to appropriate sections
                for field, value in georgian_data.items():
                    if field in ['make', 'model', 'year', 'category', 'color', 'interior_color',
                                 'interior_material', 'wheel_position', 'doors', 'seats', 'body_type', 'drive_type']:
                        listing_data["vehicle"][field] = value
                    elif field in ['fuel_type', 'displacement_liters', 'cylinders', 'transmission', 'power_hp']:
                        listing_data["engine"][field] = value
                    elif field in ['mileage_km', 'mileage_unit', 'customs_cleared', 'technical_inspection_passed', 'has_catalytic_converter']:
                        listing_data["condition"][field] = value
                    elif field in ['price', 'exchange_possible', 'negotiable', 'installment_available']:
                        listing_data["pricing"][field] = value

            # STRATEGY 1C: Try to extract data from React app embedded data
            logger.debug("[*] Attempting React data extraction...")
            react_data = MyAutoParser.extract_react_data_from_scripts(html)

            if react_data:
                logger.debug("[OK] Found React embedded data")
                # Try to extract vehicle info from React data
                # Handle different possible structures
                vehicle = react_data.get("vehicle", {})
                pricing = react_data.get("pricing", {})
                engine = react_data.get("engine", {})
                seller = react_data.get("seller", {})
                condition = react_data.get("condition", {})

                # Merge React data into listing_data
                if vehicle:
                    listing_data["vehicle"].update(vehicle)
                if pricing:
                    listing_data["pricing"].update(pricing)
                if engine:
                    listing_data["engine"].update(engine)
                if seller:
                    listing_data["seller"].update(seller)
                if condition:
                    listing_data["condition"].update(condition)

                # Try to extract at root level too (if data is flat)
                for key in ["make", "model", "year", "price", "mileage_km"]:
                    if key in react_data and key not in ["vehicle", "pricing", "condition"]:
                        if key in ["make", "model", "year"]:
                            listing_data["vehicle"][key] = react_data[key]
                        elif key == "price":
                            listing_data["pricing"][key] = react_data[key]
                        elif key == "mileage_km":
                            listing_data["condition"][key] = react_data[key]

            # STRATEGY 2: Extract from CSS selectors (fallback for non-React content)
            logger.debug("[*] Fallback: CSS selector extraction...")

            # Extract main title/heading
            title = MyAutoParser.extract_text(soup, "h1, .title, .listing-title")

            # Extract price (if not already from React)
            if not listing_data["pricing"].get("price"):
                # Try to find the main price element using Tailwind classes
                # MyAuto.ge uses: <p class="...text-[24px]...text-raisin-100...">12,500</p>
                price_selectors = [
                    'p[class*="text-[24px]"], p[class*="text-raisin-100"]',  # Tailwind main price
                    '.price, .listing-price, [data-price]',  # Common selectors
                    'p[class*="font-bold"]'  # Bold price text
                ]

                price_text = None
                for selector in price_selectors:
                    price_text = MyAutoParser.extract_text(soup, selector)
                    if price_text:
                        break

                if price_text:
                    price_data = MyAutoParser.normalize_price(price_text)
                    if price_data:
                        listing_data["pricing"]["price"] = price_data.get("price")
                        listing_data["pricing"]["currency"] = price_data.get("currency")
                        listing_data["pricing"]["currency_id"] = {"USD": 1, "GEL": 2, "EUR": 3}.get(price_data.get("currency"), 1)

                # Additionally extract both GEL and USD prices from the page
                # Store them separately for telegram notifications
                full_text = soup.get_text()
                import re

                all_prices = {}  # {amount: {'value': str, 'currency': str}}

                # Find all prices with $ or USD (these are USD)
                for match in re.finditer(r'(\d{1,3}(?:[,\s]\d{3})+|\d{4,7})\s*(?:\$|USD)', full_text, re.IGNORECASE):
                    price_raw = match.group(1)
                    price_clean = price_raw.replace(' ', '').replace(',', '')
                    if price_clean.isdigit():
                        amount = int(price_clean)
                        if 5000 < amount < 500000:  # USD range
                            if amount not in all_prices:
                                all_prices[amount] = {'value': price_raw, 'currency': 'USD'}

                # Find all prices with ₾ or GEL (these are GEL)
                for match in re.finditer(r'(\d{1,3}(?:[,\s]\d{3})+|\d{4,7})\s*(?:₾|GEL)', full_text, re.IGNORECASE):
                    price_raw = match.group(1)
                    price_clean = price_raw.replace(' ', '').replace(',', '')
                    if price_clean.isdigit():
                        amount = int(price_clean)
                        if 20000 < amount < 2000000:  # GEL range
                            if amount not in all_prices:
                                all_prices[amount] = {'value': price_raw, 'currency': 'GEL'}

                # Find all numbers in valid price range and apply logic: lowest = USD
                for match in re.finditer(r'\b(\d{4,7})\b', full_text):
                    price_raw = match.group(1)
                    amount = int(price_raw)

                    if 5000 < amount < 500000 and amount not in all_prices:
                        # Determine if this is likely USD or GEL
                        # Get surrounding context
                        context_start = max(0, match.start() - 100)
                        context_end = min(len(full_text), match.end() + 100)
                        context = full_text[context_start:context_end].lower()

                        if '$' in context or 'usd' in context:
                            all_prices[amount] = {'value': price_raw, 'currency': 'USD'}
                        elif '₾' in context or 'gel' in context:
                            all_prices[amount] = {'value': price_raw, 'currency': 'GEL'}

                # Store both USD and GEL prices for telegram
                if all_prices:
                    usd_prices = [p for p in all_prices.values() if p['currency'] == 'USD']
                    gel_prices = [p for p in all_prices.values() if p['currency'] == 'GEL']

                    # If we have both, validate with exchange rate logic (1 USD = 2.72 GEL)
                    if usd_prices and gel_prices and not listing_data["pricing"].get("price"):
                        usd_amount = min(int(p['value'].replace(',', '').replace(' ', '')) for p in usd_prices)
                        gel_amount = max(int(p['value'].replace(',', '').replace(' ', '')) for p in gel_prices)

                        # Validate exchange rate (GEL should be ~2.5-3x USD)
                        if 2.0 < gel_amount / usd_amount < 3.5:
                            listing_data["pricing"]["price_usd"] = str(usd_amount)
                            listing_data["pricing"]["price_gel"] = str(gel_amount)
                            listing_data["pricing"]["price"] = str(usd_amount)  # Primary price is USD
                            listing_data["pricing"]["currency"] = "USD"
                            listing_data["pricing"]["currency_id"] = 1
                            logger.debug(f"[PRICE] Found both: USD {usd_amount}, GEL {gel_amount}")
                    elif usd_prices and not listing_data["pricing"].get("price"):
                        usd_amount = min(int(p['value'].replace(',', '').replace(' ', '')) for p in usd_prices)
                        listing_data["pricing"]["price"] = str(usd_amount)
                        listing_data["pricing"]["price_usd"] = str(usd_amount)
                        listing_data["pricing"]["currency"] = "USD"
                        listing_data["pricing"]["currency_id"] = 1
                    elif gel_prices and not listing_data["pricing"].get("price"):
                        gel_amount = max(int(p['value'].replace(',', '').replace(' ', '')) for p in gel_prices)
                        listing_data["pricing"]["price"] = str(gel_amount)
                        listing_data["pricing"]["price_gel"] = str(gel_amount)
                        listing_data["pricing"]["currency"] = "GEL"
                        listing_data["pricing"]["currency_id"] = 2

            # Extract mileage (if not already from React)
            if not listing_data["condition"].get("mileage_km"):
                mileage_text = MyAutoParser.extract_text(soup, ".mileage, .km, [data-mileage]")
                if mileage_text:
                    listing_data["condition"]["mileage_km"] = MyAutoParser.extract_number(mileage_text)
                    listing_data["condition"]["mileage_unit"] = "km"

            # Extract vehicle specs (make, model, year) - only if not from React
            if not listing_data["vehicle"].get("make"):
                make = MyAutoParser.extract_text(soup, ".make, [data-make], .brand")
                if make:
                    listing_data["vehicle"]["make"] = make

            if not listing_data["vehicle"].get("model"):
                model = MyAutoParser.extract_text(soup, ".model, [data-model]")
                if model:
                    listing_data["vehicle"]["model"] = model

            if not listing_data["vehicle"].get("year"):
                year_text = MyAutoParser.extract_text(soup, ".year, [data-year]")
                if year_text:
                    listing_data["vehicle"]["year"] = MyAutoParser.extract_number(year_text)

            # Extract fuel type
            if not listing_data["engine"].get("fuel_type"):
                fuel = MyAutoParser.extract_text(soup, ".fuel-type, [data-fuel]")
                if fuel:
                    listing_data["engine"]["fuel_type"] = fuel.capitalize()

            # Extract transmission
            if not listing_data["engine"].get("transmission"):
                transmission = MyAutoParser.extract_text(soup, ".transmission, [data-transmission]")
                if transmission:
                    listing_data["engine"]["transmission"] = transmission.capitalize()

            # Extract location
            if not listing_data["seller"].get("location"):
                location = MyAutoParser.extract_text(soup, ".location, .region, [data-location]")
                if location:
                    listing_data["seller"]["location"] = location

            # Extract seller name
            if not listing_data["seller"].get("seller_name"):
                seller_name = MyAutoParser.extract_text(soup, ".seller-name, [data-seller], .seller")
                if seller_name:
                    listing_data["seller"]["seller_name"] = seller_name

            # Extract images
            if not listing_data["media"].get("photos"):
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
            if not listing_data["posted_date"]:
                date_text = MyAutoParser.extract_text(soup, ".posted-date, [data-posted], .date")
                if date_text:
                    listing_data["posted_date"] = date_text

            listing_data["last_updated"] = __import__("datetime").datetime.now().isoformat()

            # Extract customs cleared status
            if not listing_data["condition"].get("customs_cleared"):
                customs_text = soup.get_text().lower()
                listing_data["condition"]["customs_cleared"] = "customs" in customs_text and "cleared" in customs_text

            # FALLBACK: Extract price if not found yet
            if not listing_data["pricing"].get("price"):
                # Extract ALL prices and pick the FIRST one (appears at top of page)
                # MyAuto.ge typically displays USD price first, then GEL below
                full_text = soup.get_text()
                import re

                # Find all number patterns with their positions in the text
                prices_with_positions = []  # [(position, amount, price_str)]
                usd_prices = []  # Separate list for likely USD prices
                gel_prices = []  # Separate list for likely GEL prices

                # Pattern 1: Numbers with separators (15,500 or 15 500)
                for match in re.finditer(r'(\d{1,3}(?:[,\s]\d{3})+)', full_text):
                    price_raw = match.group(1)
                    price_clean = price_raw.replace(' ', '').replace(',', '')
                    if price_clean.isdigit():
                        amount = int(price_clean)
                        if 5000 < amount < 10000000:
                            prices_with_positions.append((match.start(), amount, price_clean))
                            # Typical USD: 5k-300k, GEL: 20k-1000k, but overlap exists
                            if amount < 300000:
                                usd_prices.append((match.start(), amount, price_clean))
                            else:
                                gel_prices.append((match.start(), amount, price_clean))

                # Pattern 2: Numbers without separators (15500, 25200, etc) - 4 to 7 digits
                for match in re.finditer(r'\b(\d{4,7})\b', full_text):
                    price_raw = match.group(1)
                    if price_raw.isdigit():
                        amount = int(price_raw)
                        if 5000 < amount < 10000000:
                            # Avoid duplicates (same amount already found)
                            if not any(p[1] == amount for p in prices_with_positions):
                                prices_with_positions.append((match.start(), amount, price_raw))
                                # Same categorization for raw numbers
                                if amount < 300000:
                                    usd_prices.append((match.start(), amount, price_raw))
                                else:
                                    gel_prices.append((match.start(), amount, price_raw))

                # Try to pick USD price first (more common), then fall back to any price
                candidate_prices = usd_prices if usd_prices else prices_with_positions

                if candidate_prices:
                    # Sort by position in text (earlier = first on page)
                    candidate_prices.sort(key=lambda x: x[0])

                    # Pick the FIRST price from candidates (appears earliest on page)
                    first_position, first_amount, price_str = candidate_prices[0]

                    listing_data["pricing"]["price"] = price_str
                    listing_data["pricing"]["currency"] = "USD"  # First price is typically USD
                    listing_data["pricing"]["currency_id"] = 1

                    all_amounts = sorted(set(p[1] for p in prices_with_positions))
                    logger.debug(f"[SMART EXTRACTION] Found prices: {all_amounts}, selected first USD candidate: {price_str}")
                else:
                    # Fallback to pattern-based extraction if no prices found
                    logger.debug("[*] No direct prices found, trying pattern-based extraction...")
                    price_found = False

                # Step 2: Pattern-based extraction if no prices found above
                if not listing_data["pricing"].get("price"):
                    gel_patterns = [
                        (r'ფასი\s*[:=]\s*([0-9\s,]+)(?:\s*(?:\$|USD))', 'Georgian label with USD'),  # Prefer if it says USD
                        (r'₾\s*(\d{1,3}(?:\s\d{3})+)', '"₾ 12 000"'),  # GEL with space-separated
                        (r'₾\s*(\d{1,3}(?:,\d{3})+)', '"₾ 12,000"'),  # GEL with comma-separated
                        (r'(\d{1,3}(?:\s\d{3})+)\s*₾', '"12 000 ₾"'),  # Space-separated ₾
                        (r'(\d{1,3}(?:,\d{3})+)\s*₾', '"12,000 ₾"'),  # Comma-separated ₾
                        (r'ფასი\s*[:=]\s*([0-9\s,]+)(?:\s*(?:\$|USD|₾|GEL))?', 'Georgian label'),  # Fallback label
                    ]

                    for pattern, desc in gel_patterns:
                        matches = re.findall(pattern, full_text)
                        if matches:
                            price_raw = matches[0]
                            price_str = price_raw.replace(' ', '').replace(',', '')

                            # Validate it's a reasonable price (3+ digits)
                            if price_str and price_str.isdigit() and len(price_str) >= 3:
                                listing_data["pricing"]["price"] = price_str
                                logger.debug(f"[FALLBACK] Extracted price: {price_str} (pattern: {desc})")

                                # Determine currency from context
                                match_pos = full_text.find(price_raw)
                                context = full_text[max(0, match_pos-100):match_pos+200]

                                if '$' in context or 'USD' in context:
                                    listing_data["pricing"]["currency"] = "USD"
                                    listing_data["pricing"]["currency_id"] = 1
                                elif '₾' in context or 'GEL' in context:
                                    listing_data["pricing"]["currency"] = "GEL"
                                    listing_data["pricing"]["currency_id"] = 2
                                else:
                                    listing_data["pricing"]["currency"] = "USD"
                                    listing_data["pricing"]["currency_id"] = 1
                                price_found = True
                                break

            # FALLBACK: Extract location if not found yet
            if not listing_data["seller"].get("location"):
                # Look for Georgian city names
                full_text = soup.get_text()
                georgian_cities = {
                    'თბილისი': 'Tbilisi',
                    'ბათუმი': 'Batumi',
                    'ქუთაისი': 'Kutaisi',
                    'გორი': 'Gori',
                    'ზუგდიდი': 'Zugdidi',
                    'სამტრედია': 'Samtredia',
                    'ჯავახეთი': 'Javakheti',
                    'წაწკერი': 'Tsagkeri',
                }

                for georgian_city, english_city in georgian_cities.items():
                    if georgian_city in full_text:
                        # Verify it's in a sensible context (not in title or very early)
                        first_occurrence = full_text.find(georgian_city)
                        if first_occurrence > 100:  # Skip early occurrences
                            listing_data["seller"]["location"] = georgian_city
                            logger.debug(f"[FALLBACK] Extracted location: {georgian_city}")
                            break

            # FALLBACK: Extract seller_name if not found yet
            if not listing_data["seller"].get("seller_name"):
                # Look for seller name patterns - usually after "გამყიდველი:" or similar
                # For now, just mark as unknown if not found
                logger.debug("[*] Seller name not found in extraction")

            # Extract description
            if not listing_data.get("description"):
                description = MyAutoParser.extract_text(
                    soup,
                    ".description, .listing-description, [data-description], .car-description"
                )

                if not description:
                    # FALLBACK 1: Look for text blocks that look like descriptions
                    # Be less restrictive - descriptions might be short or without punctuation
                    import re

                    # Known UI/metadata patterns to exclude
                    known_patterns = [
                        'მწარმოებელი', 'მოდელი', 'წელი', 'გარბენი', 'კილომეტრი',
                        'საწვავის', 'კოლოფი', 'ძრავი', 'დისკი', 'რადიატორი',
                        'შენახვა', 'შედარება', 'მიბმა', 'ნახვა', 'პირველი',
                        'ამჯამად', 'დაკეცი', 'იყიდება'
                    ]

                    # Strategy 1: Look for descriptions (not spec lists)
                    # Descriptions typically have sentence-like structure, not just lists
                    description_candidates = []

                    # Look for dedicated description sections
                    # MyAuto.ge uses: text-[14px] text-raisin-80 whitespace-pre-wrap break-words
                    desc_patterns = [
                        'div.whitespace-pre-wrap',  # Tailwind whitespace-pre-wrap class
                        '.text-raisin-80',  # Raisin color class for description text
                        '.description-section',
                        '.seller-description',
                        '.listing-description',
                        'div[data-description]'
                    ]

                    for pattern in desc_patterns:
                        elem = soup.select_one(pattern)
                        if elem:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 20:
                                description = text
                                logger.debug(f"[FALLBACK 1a] Found description in {pattern}: {text[:100]}...")
                                break

                    # Strategy 2: Look in paragraphs and divs, but only if they look like prose
                    if not description:
                        for elem in soup.find_all(['p']):  # Start with paragraphs only
                            text = elem.get_text(strip=True)

                            # Paragraphs should have natural prose characteristics
                            if (len(text) > 50 and len(text) < 1000 and
                                any('\u10A0' <= c <= '\u10FF' for c in text)):  # Has Georgian

                                # Should have sentence-like structure (punctuation)
                                has_period = '.' in text
                                has_comma = ',' in text
                                has_semicolon = ';' in text

                                # Skip if looks like a feature list (many short words without punctuation)
                                word_count = len(text.split())
                                avg_word_len = len(text.split()) / word_count if word_count > 0 else 0

                                # Real descriptions have better punctuation
                                if not (has_period or has_comma or has_semicolon):
                                    continue

                                # Skip known patterns
                                if any(pattern in text[:200] for pattern in known_patterns):
                                    continue

                                # Skip feature lists (lists of features without sentences)
                                if text.count(' ') < 10:
                                    continue

                                # This looks like a real description
                                description = text
                                logger.debug(f"[FALLBACK 1b] Found description in paragraph: {text[:100]}...")
                                break

                    # FALLBACK 2: If still not found, look for Georgian text in meta description
                    if not description:
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc:
                            meta_content = meta_desc.get('content', '')
                            if meta_content and any('\u10A0' <= c <= '\u10FF' for c in meta_content):
                                description = meta_content
                                logger.debug(f"[FALLBACK 2] Extracted description from meta: {meta_content[:100]}...")

                    # FALLBACK 3: Look in Open Graph description
                    if not description:
                        og_desc = soup.find('meta', attrs={'property': 'og:description'})
                        if og_desc:
                            og_content = og_desc.get('content', '')
                            if og_content and any('\u10A0' <= c <= '\u10FF' for c in og_content):
                                description = og_content
                                logger.debug(f"[FALLBACK 3] Extracted description from og:description: {og_content[:100]}...")

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
            logger.debug(f"    Mileage: {listing_data['condition'].get('mileage_km')}")
            logger.debug(f"    Images: {len(listing_data['media'].get('photos', []))}")

            return listing_data

        except Exception as e:
            logger.error(f"[ERROR] Error parsing listing details: {e}")
            import traceback
            logger.debug(f"    Traceback: {traceback.format_exc()}")
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
