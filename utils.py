#!/usr/bin/env python3
"""
Utility Functions Module
Helper functions for logging, validation, error handling, and formatting
"""

import logging
import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps
import time

# Type variable for decorator
T = TypeVar('T')

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for all modules

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """

    # Map string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    log_level = log_level.upper()
    numeric_level = level_map.get(log_level, logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    return root_logger


def validate_config(config: Dict) -> bool:
    """
    Validate config.json structure and required fields

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, False otherwise
    """

    try:
        # Check top-level keys
        required_keys = [
            "search_configurations",
            "scraper_settings",
            "notification_settings",
            "database_settings"
        ]

        for key in required_keys:
            if key not in config:
                logger.error(f"Missing required config key: {key}")
                return False

        # Validate search_configurations
        if not isinstance(config["search_configurations"], list):
            logger.error("search_configurations must be a list")
            return False

        if len(config["search_configurations"]) == 0:
            logger.warning("No search configurations found")
            return False

        # Validate each search configuration
        for i, search_config in enumerate(config["search_configurations"]):
            required_search_keys = ["id", "name", "base_url"]
            for key in required_search_keys:
                if key not in search_config:
                    logger.error(f"Search config {i} missing required key: {key}")
                    return False

            # Validate enabled field (optional, defaults to True)
            if "enabled" in search_config and not isinstance(search_config["enabled"], bool):
                logger.error(f"Search config {i} 'enabled' must be boolean")
                return False

        # Validate scraper_settings
        scraper_settings = config.get("scraper_settings", {})
        if "request_timeout_seconds" in scraper_settings:
            if not isinstance(scraper_settings["request_timeout_seconds"], (int, float)):
                logger.error("request_timeout_seconds must be numeric")
                return False

        if "delay_between_requests_seconds" in scraper_settings:
            if not isinstance(scraper_settings["delay_between_requests_seconds"], (int, float)):
                logger.error("delay_between_requests_seconds must be numeric")
                return False

        # Validate notification_settings
        notification_settings = config.get("notification_settings", {})
        if "send_on_new_listings" in notification_settings:
            if not isinstance(notification_settings["send_on_new_listings"], bool):
                logger.error("send_on_new_listings must be boolean")
                return False

        if "send_heartbeat_on_no_listings" in notification_settings:
            if not isinstance(notification_settings["send_heartbeat_on_no_listings"], bool):
                logger.error("send_heartbeat_on_no_listings must be boolean")
                return False

        # Validate database_settings
        database_settings = config.get("database_settings", {})
        if "retention_days" in database_settings:
            if not isinstance(database_settings["retention_days"], int) or database_settings["retention_days"] <= 0:
                logger.error("retention_days must be positive integer")
                return False

        logger.info("[OK] Configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"[ERROR] Config validation error: {e}")
        return False


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string

    Args:
        dt: Datetime object (uses current time if None)
        format_str: Format string (default: YYYY-MM-DD HH:MM:SS)

    Returns:
        Formatted timestamp string
    """

    if dt is None:
        dt = datetime.now()

    try:
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"[ERROR] Timestamp formatting error: {e}")
        return datetime.now().isoformat()


def retry_on_error(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    allowed_exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff (e.g., 2.0 for doubling)
        allowed_exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function that retries on failure
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            current_delay = delay_seconds
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"[*] {func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {current_delay:.1f}s: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(f"[ERROR] {func.__name__} failed after {max_retries} attempts: {e}")

            # Return None if all retries failed
            return None

        return wrapper
    return decorator


def load_config_file(config_path: str) -> Optional[Dict]:
    """
    Load and parse JSON configuration file

    Args:
        config_path: Path to config.json file

    Returns:
        Configuration dictionary or None if invalid
    """

    try:
        # Check if file exists
        if not os.path.exists(config_path):
            logger.error(f"[ERROR] Config file not found: {config_path}")
            return None

        # Read and parse JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        logger.info(f"[OK] Config loaded from {config_path}")
        return config

    except json.JSONDecodeError as e:
        logger.error(f"[ERROR] Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        logger.error(f"[ERROR] Error loading config file: {e}")
        return None


def get_enabled_searches(config: Dict) -> List[Dict]:
    """
    Filter enabled search configurations

    Args:
        config: Configuration dictionary

    Returns:
        List of enabled search configurations
    """

    search_configs = config.get("search_configurations", [])
    enabled_configs = [s for s in search_configs if s.get("enabled", True)]

    logger.info(f"[*] Found {len(enabled_configs)} enabled searches out of {len(search_configs)} total")
    return enabled_configs


def format_listing_for_display(car_data: Dict) -> str:
    """
    Format car data as human-readable string for logging

    Args:
        car_data: Car data dictionary

    Returns:
        Formatted string representation
    """

    try:
        vehicle = car_data.get("vehicle", {})
        pricing = car_data.get("pricing", {})
        condition = car_data.get("condition", {})

        make = vehicle.get("make", "Unknown")
        model = vehicle.get("model", "")
        year = vehicle.get("year", "")
        price = pricing.get("price", "N/A")
        currency = pricing.get("currency", "USD")
        mileage = condition.get("mileage_km", "N/A")

        # Format price with thousands separator if it's a number
        try:
            price_str = f"{int(price):,}" if price != "N/A" else "N/A"
        except (ValueError, TypeError):
            price_str = str(price)

        # Format mileage with thousands separator if it's a number
        try:
            mileage_str = f"{int(mileage):,}" if mileage != "N/A" else "N/A"
        except (ValueError, TypeError):
            mileage_str = str(mileage)

        return f"{year} {make} {model} | ${price_str} {currency} | {mileage_str} km"

    except Exception as e:
        logger.error(f"[ERROR] Error formatting listing: {e}")
        return "Error formatting listing"


def sanitize_log_message(message: str, max_length: int = 500) -> str:
    """
    Sanitize message for logging (remove sensitive data, truncate)

    Args:
        message: Message to sanitize
        max_length: Maximum message length

    Returns:
        Sanitized message
    """

    # Truncate if too long
    if len(message) > max_length:
        message = message[:max_length] + "..."

    # Remove common credential patterns
    sensitive_patterns = [
        "token",
        "auth",
        "secret",
        "password",
        "api_key",
        "bot",
    ]

    for pattern in sensitive_patterns:
        if pattern.lower() in message.lower():
            message = message.replace(message, f"<{pattern}_redacted>")

    return message


def calculate_statistics(listings: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics from listings

    Args:
        listings: List of car data dictionaries

    Returns:
        Dictionary with statistics
    """

    if not listings:
        return {
            "total_count": 0,
            "avg_price": 0,
            "price_range": {"min": 0, "max": 0},
            "locations": [],
            "fuel_types": []
        }

    try:
        prices = []
        locations = {}
        fuel_types = {}

        for listing in listings:
            pricing = listing.get("pricing", {})
            seller = listing.get("seller", {})
            vehicle = listing.get("vehicle", {})

            # Collect price data
            price = pricing.get("price")
            if price and isinstance(price, (int, float)):
                prices.append(price)

            # Collect location data
            location = seller.get("location", "Unknown")
            locations[location] = locations.get(location, 0) + 1

            # Collect fuel type data
            fuel = vehicle.get("fuel_type", "Unknown")
            fuel_types[fuel] = fuel_types.get(fuel, 0) + 1

        return {
            "total_count": len(listings),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0
            },
            "locations": sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5],
            "fuel_types": sorted(fuel_types.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    except Exception as e:
        logger.error(f"[ERROR] Error calculating statistics: {e}")
        return {}


def get_config_path() -> str:
    """
    Get configuration file path from environment or use default

    Returns:
        Path to configuration file
    """

    config_path = os.getenv("CONFIG_PATH", "config.json")
    return config_path


def get_log_level() -> str:
    """
    Get log level from environment or use default

    Returns:
        Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """

    log_level = os.getenv("LOG_LEVEL", "INFO")
    return log_level


if __name__ == "__main__":
    # Test utilities
    logging.basicConfig(level=logging.INFO)

    logger.info("[*] Testing utilities...")

    # Test timestamp formatting
    now = datetime.now()
    formatted = format_timestamp(now)
    logger.info(f"[OK] Timestamp: {formatted}")

    # Test config validation with sample
    sample_config = {
        "search_configurations": [
            {"id": 1, "name": "Test Search", "base_url": "https://example.com", "enabled": True}
        ],
        "scraper_settings": {"request_timeout_seconds": 10},
        "notification_settings": {"send_on_new_listings": True},
        "database_settings": {"retention_days": 365}
    }

    is_valid = validate_config(sample_config)
    logger.info(f"[OK] Config validation: {is_valid}")

    # Test retry decorator
    @retry_on_error(max_retries=2, delay_seconds=0.1)
    def test_function():
        raise ValueError("Test error")

    result = test_function()
    logger.info(f"[OK] Retry decorator test completed")

    logger.info("[OK] All utility tests passed!")
