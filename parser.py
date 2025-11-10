#!/usr/bin/env python3
"""
Parser Utilities - Extract data from HTML/JSON
Helper functions for scraping MyAuto.ge listings
"""

import re
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class MyAutoParser:
    """Parse MyAuto.ge HTML/JSON data into structured format"""

    @staticmethod
    def extract_text(element, selector: str, default: str = None) -> Optional[str]:
        """
        Extract text from element using CSS selector

        Args:
            element: BeautifulSoup element
            selector: CSS selector string
            default: Default value if not found

        Returns:
            Extracted text or default
        """

        try:
            if not element:
                return default

            found = element.select_one(selector)
            if found:
                text = found.get_text(strip=True)
                return text if text else default

            return default

        except Exception as e:
            logger.debug(f"Error extracting text: {e}")
            return default

    @staticmethod
    def extract_attribute(element, selector: str, attribute: str,
                         default: str = None) -> Optional[str]:
        """
        Extract attribute from element using CSS selector

        Args:
            element: BeautifulSoup element
            selector: CSS selector string
            attribute: Attribute name (href, src, data-*, etc)
            default: Default value if not found

        Returns:
            Extracted attribute or default
        """

        try:
            if not element:
                return default

            found = element.select_one(selector)
            if found:
                attr = found.get(attribute)
                return attr if attr else default

            return default

        except Exception as e:
            logger.debug(f"Error extracting attribute: {e}")
            return default

    @staticmethod
    def extract_number(text: str, default: int = None) -> Optional[int]:
        """
        Extract first number from text

        Args:
            text: Text containing number
            default: Default value if not found

        Returns:
            Extracted number or default
        """

        try:
            if not text:
                return default

            # Remove spaces and commas
            text = text.replace(" ", "").replace(",", "")

            # Find first number
            match = re.search(r"\d+", text)
            if match:
                return int(match.group())

            return default

        except Exception as e:
            logger.debug(f"Error extracting number: {e}")
            return default

    @staticmethod
    def extract_float(text: str, default: float = None) -> Optional[float]:
        """
        Extract float number from text

        Args:
            text: Text containing number
            default: Default value if not found

        Returns:
            Extracted float or default
        """

        try:
            if not text:
                return default

            # Remove spaces
            text = text.replace(" ", "").replace(",", ".")

            # Find float number
            match = re.search(r"\d+\.?\d*", text)
            if match:
                return float(match.group())

            return default

        except Exception as e:
            logger.debug(f"Error extracting float: {e}")
            return default

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """
        Clean multiple whitespaces and newlines

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """

        if not text:
            return ""

        # Replace multiple spaces/newlines with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def extract_url(element, selector: str, base_url: str = None,
                   default: str = None) -> Optional[str]:
        """
        Extract and normalize URL from element

        Args:
            element: BeautifulSoup element
            selector: CSS selector
            base_url: Base URL for relative links
            default: Default if not found

        Returns:
            Absolute URL or default
        """

        try:
            if not element:
                return default

            found = element.select_one(selector)
            if not found:
                return default

            href = found.get("href")
            if not href:
                return default

            # Handle relative URLs
            if not href.startswith("http"):
                if base_url:
                    href = base_url.rstrip("/") + "/" + href.lstrip("/")
                else:
                    href = "https://www.myauto.ge" + ("/" if not href.startswith("/") else "") + href

            return href

        except Exception as e:
            logger.debug(f"Error extracting URL: {e}")
            return default

    @staticmethod
    def extract_listing_id(url: str) -> Optional[str]:
        """
        Extract listing ID from MyAuto.ge URL

        Args:
            url: MyAuto.ge URL

        Returns:
            Listing ID or None
        """

        try:
            if not url:
                return None

            # URL format: https://www.myauto.ge/ka/pr/119084515/...
            match = re.search(r"/pr/(\d+)", url)
            if match:
                return match.group(1)

            return None

        except Exception as e:
            logger.debug(f"Error extracting listing ID: {e}")
            return None

    @staticmethod
    def normalize_price(price_text: str, currency: str = "USD") -> Optional[Dict]:
        """
        Parse price text and extract amount + currency

        Args:
            price_text: Price text (e.g., "$15,500" or "15500 USD")
            currency: Default currency

        Returns:
            Dict with price and currency or None
        """

        try:
            if not price_text:
                return None

            # Try to detect currency
            detected_currency = currency
            if "USD" in price_text.upper() or "$" in price_text:
                detected_currency = "USD"
            elif "GEL" in price_text.upper() or "₾" in price_text:
                detected_currency = "GEL"
            elif "EUR" in price_text.upper() or "€" in price_text:
                detected_currency = "EUR"

            # Extract number
            price = MyAutoParser.extract_number(price_text)

            if price:
                return {
                    "price": price,
                    "currency": detected_currency
                }

            return None

        except Exception as e:
            logger.debug(f"Error normalizing price: {e}")
            return None

    @staticmethod
    def parse_listing_summary(listing_element) -> Optional[Dict]:
        """
        Parse listing card from search results

        Args:
            listing_element: BeautifulSoup element for listing card

        Returns:
            Dict with summary data or None
        """

        try:
            if not listing_element:
                return None

            # Extract URL to get listing ID
            url = MyAutoParser.extract_url(
                listing_element,
                "a[href*='/pr/']",
                base_url="https://www.myauto.ge"
            )

            if not url:
                return None

            listing_id = MyAutoParser.extract_listing_id(url)
            if not listing_id:
                return None

            # Extract basic info from card
            title = MyAutoParser.extract_text(listing_element, ".listing-title, h2, .title")
            price_text = MyAutoParser.extract_text(listing_element, ".price, .listing-price")
            location = MyAutoParser.extract_text(listing_element, ".location, .region")
            mileage_text = MyAutoParser.extract_text(listing_element, ".mileage, .km")
            image_url = MyAutoParser.extract_attribute(listing_element, "img", "src")

            price_data = MyAutoParser.normalize_price(price_text) if price_text else None

            return {
                "listing_id": listing_id,
                "url": url,
                "title": title,
                "price": price_data.get("price") if price_data else None,
                "currency": price_data.get("currency") if price_data else "USD",
                "location": location,
                "mileage_km": MyAutoParser.extract_number(mileage_text) if mileage_text else None,
                "image_url": image_url
            }

        except Exception as e:
            logger.debug(f"Error parsing listing summary: {e}")
            return None

    @staticmethod
    def parse_html_to_dict(html: str) -> Dict[str, Any]:
        """
        Parse HTML string to BeautifulSoup object

        Args:
            html: HTML content

        Returns:
            Dict with soup and structure info
        """

        try:
            soup = BeautifulSoup(html, "lxml")

            return {
                "soup": soup,
                "title": soup.title.string if soup.title else None,
                "is_valid": bool(soup.body)
            }

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return {
                "soup": None,
                "title": None,
                "is_valid": False
            }

    @staticmethod
    def extract_json_from_html(html: str, script_type: str = "application/ld+json") -> Optional[Dict]:
        """
        Extract JSON-LD structured data from HTML

        Args:
            html: HTML content
            script_type: Script type (usually application/ld+json)

        Returns:
            Parsed JSON dict or None
        """

        try:
            soup = BeautifulSoup(html, "lxml")

            # Find script tags with JSON-LD
            scripts = soup.find_all("script", {"type": script_type})

            if scripts:
                import json
                # Try to parse first script
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        return data
                    except:
                        continue

            return None

        except Exception as e:
            logger.debug(f"Error extracting JSON from HTML: {e}")
            return None

    @staticmethod
    def extract_vehicle_from_heading(soup) -> Optional[Dict]:
        """
        Extract vehicle info from heading element
        MyAuto.ge displays vehicle as "YEAR MAKE MODEL" in h6 heading

        Args:
            soup: BeautifulSoup object

        Returns:
            Dict with vehicle data or None
        """
        try:
            # Look for h6 with vehicle info (format: "2001 Toyota Land Cruiser")
            h6 = soup.find("h6")
            if not h6:
                return None

            text = h6.get_text(strip=True)
            if not text:
                return None

            logger.debug(f"[*] Found heading text: {text[:50]}")

            # Parse format: "YEAR MAKE MODEL"
            # Example: "2001 Toyota Land Cruiser"
            parts = text.split()

            vehicle_data = {}

            if len(parts) >= 3:
                # First part is usually year
                try:
                    year = int(parts[0])
                    vehicle_data["year"] = year
                    logger.debug(f"[OK] Extracted year: {year}")
                except:
                    pass

                # Make is typically next (usually 1 word: Toyota, Honda, BMW, etc)
                if len(parts) >= 2:
                    make = parts[1]
                    vehicle_data["make"] = make
                    logger.debug(f"[OK] Extracted make: {make}")

                # Model is the rest (can be multiple words: Land Cruiser, Range Rover, etc)
                if len(parts) >= 3:
                    model = " ".join(parts[2:])
                    vehicle_data["model"] = model
                    logger.debug(f"[OK] Extracted model: {model}")

            return vehicle_data if vehicle_data else None

        except Exception as e:
            logger.debug(f"Error extracting vehicle from heading: {e}")
            return None

    @staticmethod
    def extract_georgian_labeled_fields(soup) -> Optional[Dict]:
        """
        Extract vehicle fields from Georgian-labeled divs
        Handles structure: divs containing "label:value" text
        All values returned as strings for VARCHAR compatibility

        Args:
            soup: BeautifulSoup object

        Returns:
            Dict with extracted fields or None
        """
        try:
            data = {}

            # Georgian label to field mapping
            label_mapping = {
                'მწარმოებელი': 'make',
                'მოდელი': 'model',
                'წელი': 'year',
                'კატეგორია': 'category',
                'გარბენი': 'mileage_km',
                'საწვავის ტიპი': 'fuel_type',
                'ძრავის მოცულობა': 'displacement_liters',
                'ძრავი': 'displacement_liters',
                'ცილინდრები': 'cylinders',
                'გადაცემათა კოლოფი': 'transmission',
                'კოლოფი': 'transmission',
                'წამყვანი თვლები': 'drive_type',
                'კარები': 'doors',
                'აირბეგი': 'seats',
                'საჭე': 'wheel_position',
                'ფერი': 'color',
                'სალონის ფერი': 'interior_color',
                'სალონის მასალა': 'interior_material',
                'ფასი': 'price',
                'განბაჟება': 'customs_cleared',
                'ტექ. დათვალიერება': 'technical_inspection_passed',
                'კატალიზატორი': 'has_catalytic_converter',
                'გაცვლა': 'exchange_possible',
            }

            # Find all divs that contain Georgian labels with colons
            divs = soup.find_all('div')

            for div in divs:
                text = div.get_text(strip=True)

                # Only process if it contains a colon
                if ':' not in text:
                    continue

                # Split on first colon
                parts = text.split(':', 1)
                if len(parts) != 2:
                    continue

                label = parts[0].strip()
                value = parts[1].strip()

                # Skip if empty
                if not label or not value:
                    continue

                # Check if this is a known Georgian label
                if label not in label_mapping:
                    continue

                field_name = label_mapping[label]

                # Don't overwrite if already found
                if field_name in data:
                    continue

                # For some fields, extract just the number
                if field_name in ['mileage_km', 'displacement_liters', 'cylinders', 'doors', 'seats', 'price', 'year']:
                    match = re.search(r'\d+\.?\d*', value)
                    if match:
                        value = match.group(0)

                # Store as string
                data[field_name] = value
                logger.debug(f"[OK] Extracted {field_name}: {value}")

            return data if data else None

        except Exception as e:
            logger.debug(f"Error extracting Georgian labeled fields: {e}")
            return None

    @staticmethod
    def extract_react_data_from_scripts(html: str) -> Optional[Dict]:
        """
        Extract data embedded in React app script tags
        MyAuto.ge embeds listing data in script tags for SEO/React hydration

        Args:
            html: HTML content

        Returns:
            Parsed data dict or None
        """

        try:
            import json
            soup = BeautifulSoup(html, "lxml")

            # Find all script tags without type attribute (often contains app state)
            scripts = soup.find_all("script")

            for script in scripts:
                if not script.string:
                    continue

                script_content = script.string

                # Look for JSON patterns in script content
                # Common patterns: "listing":{...}, "vehicle":{...}, "__INITIAL_STATE__"
                if "listing" not in script_content.lower() and "vehicle" not in script_content.lower():
                    continue

                # Try to extract JSON from script content
                # Look for patterns like: {..."listing":{...}} or {..."vehicle":{...}}
                try:
                    # Try to find and parse JSON objects
                    # Handle both wrapped and unwrapped JSON

                    # First, try to parse the entire script as JSON
                    try:
                        data = json.loads(script_content)
                        if isinstance(data, dict):
                            logger.debug(f"[OK] Extracted JSON from script tag ({len(script_content)} chars)")
                            return data
                    except:
                        pass

                    # Try to find JSON object patterns
                    # Look for {...} patterns containing listing/vehicle data
                    import re
                    json_patterns = [
                        r'\{[^{}]*"listing"[^{}]*\}',
                        r'\{[^{}]*"vehicle"[^{}]*\}',
                        r'\{[^{}]*"make"[^{}]*\}',
                    ]

                    for pattern in json_patterns:
                        matches = re.findall(pattern, script_content)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                if isinstance(data, dict) and any(k in data for k in ["listing", "vehicle", "make"]):
                                    logger.debug(f"[OK] Found data pattern in script: {list(data.keys())}")
                                    return data
                            except:
                                continue

                except Exception as e:
                    logger.debug(f"[*] Could not parse script content: {e}")
                    continue

            logger.debug("[*] No React data found in script tags")
            return None

        except Exception as e:
            logger.debug(f"Error extracting React data: {e}")
            return None


def test_parser():
    """Test parser functions"""

    logger.info("Testing parser...")

    # Test number extraction
    assert MyAutoParser.extract_number("250,000 km") == 250000
    assert MyAutoParser.extract_float("3.0L") == 3.0
    logger.info("[OK] Number extraction works")

    # Test price normalization
    price = MyAutoParser.normalize_price("$15,500")
    assert price["price"] == 15500
    assert price["currency"] == "USD"
    logger.info("[OK] Price normalization works")

    # Test URL extraction
    url = "https://www.myauto.ge/ka/pr/119084515/listing"
    listing_id = MyAutoParser.extract_listing_id(url)
    assert listing_id == "119084515"
    logger.info("[OK] Listing ID extraction works")

    logger.info("[OK] All parser tests passed!")
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(0 if test_parser() else 1)
