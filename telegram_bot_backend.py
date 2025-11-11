#!/usr/bin/env python3
"""
Telegram Bot Backend
Handles bot commands and user interactions via Telegram Bot API
Commands: /set <url>, /list, /clear, /help, /status
"""

import os
import logging
import requests
import time
import warnings
import urllib3
from typing import Dict, Optional, List, Any
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

# Suppress SSL warnings for test environments (handles corporate proxies, etc.)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Import notification formatter for consistent formatting
try:
    from notifications_telegram import TelegramNotificationManager
except ImportError:
    TelegramNotificationManager = None


class TelegramBotBackend:
    """Telegram Bot for managing MyAuto search subscriptions"""

    # Telegram Bot API endpoints
    BASE_API_URL = "https://api.telegram.org"

    def __init__(self, bot_token: str = None, database = None, scraper = None, config = None, verify_ssl: bool = True):
        """
        Initialize Telegram Bot

        Args:
            bot_token: Telegram bot token (from environment if None)
            database: Database instance for storing subscriptions
            scraper: MyAutoScraper instance for reference (for initialization check only)
            config: Configuration dict for scraper (needed to create fresh instances for /run)
            verify_ssl: Whether to verify SSL certificates (default True, False for corporate proxies)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.database = database
        self.scraper = scraper  # Reference to original scraper (may be None)
        self.config = config  # Used to create fresh scraper instances for /run (avoids threading issues)
        self.verify_ssl = verify_ssl

        if not self.bot_token:
            logger.error("[ERROR] TELEGRAM_BOT_TOKEN not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        self.api_url = f"{self.BASE_API_URL}/bot{self.bot_token}"
        self.last_update_id = 0
        self.allowed_chats = set()  # Can be extended for security

        logger.info("[*] Telegram Bot Backend initialized")

    def set_allowed_chats(self, chat_ids: List[int]):
        """
        Set list of allowed chat IDs (optional security feature)

        Args:
            chat_ids: List of allowed Telegram chat IDs
        """
        self.allowed_chats = set(chat_ids)
        logger.info(f"[*] Allowed chats restricted to: {self.allowed_chats}")

    def is_chat_allowed(self, chat_id: int) -> bool:
        """
        Check if a chat is allowed to use the bot

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if allowed (or no restrictions)
        """
        if not self.allowed_chats:
            return True  # No restrictions
        return chat_id in self.allowed_chats

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with SSL error handling

        If SSL verification fails (common with corporate proxies),
        automatically retry without verification

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests

        Returns:
            requests.Response object
        """
        try:
            # First attempt with SSL verification
            kwargs['verify'] = self.verify_ssl
            return requests.request(method, url, **kwargs)

        except requests.exceptions.SSLError as ssl_error:
            # If SSL fails and verification is enabled, retry without it
            if self.verify_ssl:
                logger.warning(f"[WARN] SSL verification failed, retrying without verification")
                logger.warning(f"[WARN] This may indicate a corporate proxy or firewall")
                self.verify_ssl = False  # Disable for future requests
                kwargs['verify'] = False
                return requests.request(method, url, **kwargs)
            else:
                raise

    def send_message(self, chat_id: int, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a text message to user

        Args:
            chat_id: Telegram chat ID
            message: Message text
            parse_mode: "HTML" or "Markdown"

        Returns:
            True if sent successfully
        """
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode
            }

            response = self._make_request('POST', url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"[OK] Message sent to chat {chat_id}")
                    return True
                else:
                    logger.error(f"[ERROR] Telegram error: {result.get('description')}")
                    return False
            else:
                logger.error(f"[ERROR] HTTP {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Failed to send message: {e}")
            return False

    def get_updates(self, timeout: int = 30) -> List[Dict]:
        """
        Get updates from Telegram using long polling

        Args:
            timeout: Long polling timeout in seconds

        Returns:
            List of update dictionaries
        """
        try:
            url = f"{self.api_url}/getUpdates"
            payload = {
                "offset": self.last_update_id + 1,
                "timeout": timeout
            }

            response = self._make_request('POST', url, json=payload, timeout=timeout + 5)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    updates = result.get("result", [])
                    if updates:
                        # Update the last_update_id for next poll
                        self.last_update_id = updates[-1]["update_id"]
                        logger.debug(f"[*] Received {len(updates)} updates")
                    return updates
                else:
                    logger.error(f"[ERROR] Telegram error: {result.get('description')}")
                    return []
            else:
                logger.error(f"[ERROR] HTTP {response.status_code}: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] Failed to get updates: {e}")
            return []

    def process_message(self, message: Dict) -> bool:
        """
        Process incoming message and execute appropriate command

        Args:
            message: Message dictionary from Telegram

        Returns:
            True if processed successfully
        """
        try:
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "").strip()

            if not chat_id or not text:
                return False

            # Check if chat is allowed
            if not self.is_chat_allowed(chat_id):
                logger.warning(f"[!] Unauthorized chat attempt: {chat_id}")
                self.send_message(chat_id, "❌ You are not authorized to use this bot.")
                return False

            logger.info(f"[*] Message from chat {chat_id}: {text[:100]}")

            # Parse command
            parts = text.split(maxsplit=1)
            command = parts[0].lower()

            # Route to appropriate handler
            if command == "/start" or command == "/help":
                return self._handle_help(chat_id)
            elif command == "/set":
                url = parts[1] if len(parts) > 1 else None
                return self._handle_set(chat_id, url)
            elif command == "/list":
                return self._handle_list(chat_id)
            elif command == "/clear":
                argument = parts[1] if len(parts) > 1 else None
                return self._handle_clear(chat_id, argument)
            elif command == "/status":
                return self._handle_status(chat_id)
            elif command == "/run":
                sub_number = parts[1] if len(parts) > 1 else None
                return self._handle_run(chat_id, sub_number)
            elif command == "/reset":
                sub_number = parts[1] if len(parts) > 1 else None
                return self._handle_reset(chat_id, sub_number)
            else:
                # Unknown command - show help
                return self._handle_help(chat_id)

        except Exception as e:
            logger.error(f"[ERROR] Error processing message: {e}")
            chat_id = message.get("chat", {}).get("id")
            if chat_id:
                self.send_message(chat_id, "❌ An error occurred processing your request. Please try again.")
            return False

    def _handle_help(self, chat_id: int) -> bool:
        """
        Handle /start and /help commands

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if sent successfully
        """
        help_text = """
<b>🚗 MyAuto Search Bot</b>

This bot helps you monitor MyAuto.ge car listings. Set search URLs and get notified when new listings appear!

<b>Available Commands:</b>

/set &lt;url&gt;
  Save a MyAuto search URL to monitor
  <i>Example: /set https://www.myauto.ge/ka/search?...</i>

/list
  Show all your saved searches

/run &lt;number&gt;
  🚀 Immediately check a saved search for new listings
  <i>Example: /run 1 (checks first saved search)</i>

/reset &lt;number&gt;
  🗑️ Clear tracking history for a specific search
  <i>Example: /reset 1 (resets memory for first search)</i>
  The bot will show all listings as "new" on next check

/clear &lt;all | number&gt;
  Remove saved search(es)
  <i>Example: /clear all (removes all searches)</i>
  <i>Example: /clear 1 (removes first search)</i>

/status
  Show bot statistics

/help
  Show this help message

<b>How it works:</b>
1. Create a search on MyAuto.ge with your filters (make, model, price, etc.)
2. Copy the search URL
3. Send /set &lt;URL&gt; to save it
4. Use /run 1, /run 2, etc. to check immediately
5. The bot will also check periodically and notify you of new listings
6. Use /reset 1, /reset 2, etc. to clear the "already seen" memory
7. Use /clear 1, /clear 2, or /clear all to remove searches

<b>🔔 Notifications:</b>
You'll receive a message when new car listings matching your criteria are found!

<b>Questions?</b>
Make sure your MyAuto.ge search URL is complete and accurate.
"""
        return self.send_message(chat_id, help_text)

    def _handle_set(self, chat_id: int, url: str) -> bool:
        """
        Handle /set command to add a search URL

        Args:
            chat_id: Telegram chat ID
            url: MyAuto search URL

        Returns:
            True if processed successfully
        """
        if not url:
            message = "❌ <b>Error:</b> Please provide a URL\n\n<i>/set &lt;MyAuto.ge search URL&gt;</i>"
            return self.send_message(chat_id, message)

        # Validate URL
        if not self._is_valid_myauto_url(url):
            message = """❌ <b>Invalid URL</b>

The URL must be from MyAuto.ge. Examples:
  https://www.myauto.ge/ka/search?...
  https://myauto.ge/ka/search?...

<b>How to get the URL:</b>
1. Open MyAuto.ge in your browser
2. Set your search filters (make, model, price, etc.)
3. Copy the URL from the address bar
4. Send it with: /set &lt;URL&gt;"""
            return self.send_message(chat_id, message)

        # Try to add subscription
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        # Get or create user for this chat_id
        user_id = self.database.get_or_create_telegram_user(chat_id)
        if not user_id:
            logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
            return self.send_message(chat_id, "❌ Failed to create user. Please try again later.")

        # Add subscription for this user
        success, error_msg = self.database.add_subscription(user_id, url)

        if success:
            message = f"""✅ <b>Search criteria saved!</b>

URL: <code>{url}</code>

I'll check this search periodically and notify you when new listings appear. 🔔

Use /list to see all your saved searches."""
            return self.send_message(chat_id, message)
        else:
            # Determine if it's a duplicate or real error
            if "already exists" in (error_msg or "").lower():
                message = f"""⚠️ <b>Already monitoring</b>

This URL is already in your saved searches.

Use /list to see all your searches."""
            else:
                message = f"""❌ <b>Error adding search</b>

{error_msg or 'Please try again later.'}

Use /list to see your current searches."""
            return self.send_message(chat_id, message)

    def _handle_list(self, chat_id: int) -> bool:
        """
        Handle /list command to show saved searches

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if processed successfully
        """
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        # Get or create user for this chat_id
        user_id = self.database.get_or_create_telegram_user(chat_id)
        if not user_id:
            logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
            return self.send_message(chat_id, "❌ Failed to retrieve user. Please try again later.")

        subscriptions = self.database.get_subscriptions(user_id)

        if not subscriptions:
            message = """📋 <b>Your saved searches:</b>

You haven't saved any searches yet.

<b>To add a search:</b>
1. Go to MyAuto.ge and create your search
2. Copy the URL
3. Send: /set &lt;URL&gt;"""
            return self.send_message(chat_id, message)

        # Format subscriptions
        message = "<b>📋 Your saved searches:</b>\n\n"

        for i, sub in enumerate(subscriptions, 1):
            url = sub.get("search_url", "")
            created = sub.get("created_at", "")
            last_checked = sub.get("last_checked") or "Never"

            # Extract readable search details from URL
            search_details = self._extract_search_details(url)

            message += f"<b>{i}. {search_details}</b>\n"
            message += f"   📅 Added: {created}\n"
            message += f"   ⏰ Last checked: {last_checked}\n"
            message += f"   🔗 <code>{self._shorten_url(url, max_length=40)}</code>\n\n"

        message += f"<b>Total:</b> {len(subscriptions)} search(es)\n"
        message += "\n💡 Use /run 1, /run 2, etc. to check a search\n"
        message += "🗑️ Use /reset 1, /reset 2, etc. to clear tracking\n"
        message += "❌ Use /clear 1, /clear 2, etc. to remove specific\n"
        message += "❌ Use /clear all to remove all searches"

        return self.send_message(chat_id, message)

    def _handle_clear(self, chat_id: int, argument: str = None) -> bool:
        """
        Handle /clear command to remove saved searches

        Args:
            chat_id: Telegram chat ID
            argument: Optional argument - "all" to clear all, or search number to clear specific

        Returns:
            True if processed successfully
        """
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        # Get or create user for this chat_id
        user_id = self.database.get_or_create_telegram_user(chat_id)
        if not user_id:
            logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
            return self.send_message(chat_id, "❌ Failed to retrieve user. Please try again later.")

        # Get current subscriptions
        subscriptions = self.database.get_subscriptions(user_id)
        count = len(subscriptions)

        if count == 0:
            message = "📋 You don't have any saved searches to clear."
            return self.send_message(chat_id, message)

        # If no argument provided, show help
        if not argument:
            message = f"""❓ <b>Clear searches - Usage:</b>

You have {count} saved search(es).

<b>Options:</b>
/clear all
  Remove all {count} searches

/clear 1
  Remove only search #1

/clear 2
  Remove only search #2

etc.

<b>Example:</b>
/clear 1  (removes first search)
/clear all  (removes all searches)"""
            return self.send_message(chat_id, message)

        # Handle "all" argument
        if argument.lower() == "all":
            success, error_msg = self.database.clear_subscriptions(user_id)

            if success:
                message = f"""✅ <b>All searches cleared!</b>

Removed {count} search(es) from monitoring.

To add new searches:
/set &lt;MyAuto.ge URL&gt;"""
                return self.send_message(chat_id, message)
            else:
                message = "❌ Failed to clear searches. Please try again."
                return self.send_message(chat_id, message)

        # Handle specific search number
        try:
            sub_index = int(argument) - 1

            if sub_index < 0:
                message = "❌ <b>Error:</b> Search number must be 1 or higher"
                return self.send_message(chat_id, message)

            if sub_index >= len(subscriptions):
                message = f"❌ <b>Error:</b> You only have {len(subscriptions)} search(es).\n\nUse /list to see all searches."
                return self.send_message(chat_id, message)

            # Get the subscription to delete
            subscription = subscriptions[sub_index]
            subscription_id = subscription.get("id")

            # Delete the specific subscription
            success, error_msg = self.database.delete_subscription(user_id, subscription_id)

            if success:
                search_details = self._extract_search_details(subscription.get("search_url", ""))
                message = f"""✅ <b>Search removed!</b>

Deleted: {search_details}

Remaining searches: {len(subscriptions) - 1}

Use /list to see your current searches."""
                return self.send_message(chat_id, message)
            else:
                message = f"❌ Failed to remove search. {error_msg or 'Please try again.'}"
                return self.send_message(chat_id, message)

        except ValueError:
            message = "❌ <b>Error:</b> Invalid argument\n\n<b>Usage:</b>\n/clear all\n/clear 1\n/clear 2\n\netc."
            return self.send_message(chat_id, message)

        except Exception as e:
            logger.error(f"[ERROR] Error in /clear command: {e}")
            return self.send_message(chat_id, "❌ An error occurred. Please try again.")

    def _handle_status(self, chat_id: int) -> bool:
        """
        Handle /status command to show statistics

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if processed successfully
        """
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        try:
            # Get or create user for this chat_id
            user_id = self.database.get_or_create_telegram_user(chat_id)
            if not user_id:
                logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
                return self.send_message(chat_id, "❌ Failed to retrieve user. Please try again later.")

            stats = self.database.get_statistics()
            user_subs = self.database.get_subscriptions(user_id)

            message = f"""<b>📊 Bot Statistics</b>

<b>Your Status:</b>
• Active searches: {len(user_subs)}

<b>Overall Statistics:</b>
• Active users: {stats.get('total_users', 0)}
• Total searches: {stats.get('total_subscriptions', 0)}
• Listings tracked: {stats.get('total_seen_listings', 0)}

<b>Server Status:</b> ✅ Online and monitoring

Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            return self.send_message(chat_id, message)

        except Exception as e:
            logger.error(f"[ERROR] Failed to get status: {e}")
            return self.send_message(chat_id, "❌ Failed to retrieve status. Please try again.")

    def _handle_run(self, chat_id: int, sub_number: str) -> bool:
        """
        Handle /run command to immediately check a specific subscription

        Args:
            chat_id: Telegram chat ID
            sub_number: Subscription number (1-based index) as string

        Returns:
            True if processed successfully
        """
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        if not sub_number:
            message = "❌ <b>Error:</b> Please specify which search to run\n\n<i>/run 1</i> - checks first search\n<i>/run 2</i> - checks second search"
            return self.send_message(chat_id, message)

        try:
            # Get or create user for this chat_id
            user_id = self.database.get_or_create_telegram_user(chat_id)
            if not user_id:
                logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
                return self.send_message(chat_id, "❌ Failed to retrieve user. Please try again later.")

            # Convert sub_number to integer (1-based index)
            sub_index = int(sub_number) - 1

            if sub_index < 0:
                message = "❌ <b>Error:</b> Search number must be 1 or higher"
                return self.send_message(chat_id, message)

            # Get subscriptions for this user
            subscriptions = self.database.get_subscriptions(user_id)

            if not subscriptions:
                message = "📋 You don't have any saved searches.\n\nUse /set to add a search."
                return self.send_message(chat_id, message)

            if sub_index >= len(subscriptions):
                message = f"❌ <b>Error:</b> You only have {len(subscriptions)} search(es).\n\nUse /list to see all searches."
                return self.send_message(chat_id, message)

            # Get the requested subscription
            subscription = subscriptions[sub_index]
            search_url = subscription.get("search_url")
            sub_id = subscription.get("id")

            logger.info(f"[*] Running immediate check for subscription {sub_id}: {search_url[:80]}")

            # Send "checking" status
            self.send_message(chat_id, "⏳ Checking for new listings... (this may take a moment)")

            # Create a fresh scraper instance for /run to avoid threading issues
            # (gevent/async operations are tied to the thread they were created in)
            if not self.config:
                logger.error("[ERROR] Configuration not available for /run command")
                return self.send_message(chat_id, "❌ Search functionality not available. Please try again later.")

            try:
                # Import here to avoid circular imports
                from scraper import MyAutoScraper

                # Create fresh scraper instance (avoid threading/greenlet issues)
                scraper = MyAutoScraper(self.config)

                search_config = {
                    "base_url": search_url,
                    "parameters": {}
                }

                # Run scraper in thread pool to avoid Playwright asyncio conflicts
                # Playwright sync API doesn't work inside asyncio event loops,
                # so we run it in a separate thread with its own event loop context
                with ThreadPoolExecutor(max_workers=1) as executor:
                    listings = executor.submit(scraper.fetch_search_results, search_config).result(timeout=30)

                if not listings:
                    message = f"<b>✅ Check Complete</b>\n\nNo new listings found for search #{sub_index + 1}.\n\n<code>{search_url[:60]}...</code>"
                    return self.send_message(chat_id, message)

                # Filter for new listings (not seen before)
                new_listings = []

                for listing in listings:
                    listing_id = listing.get("listing_id")

                    if listing_id and not self.database.has_user_seen_listing(user_id, listing_id):
                        new_listings.append(listing)
                        # Mark as seen
                        self.database.mark_listing_seen(user_id, listing_id)
                        logger.debug(f"[*] New listing marked: {listing_id}")

                if new_listings:
                    logger.info(f"[+] Found {len(new_listings)} new listings for subscription {sub_id}")

                    # Format and send results
                    if len(new_listings) == 1:
                        message = self._format_single_listing_for_run(new_listings[0], sub_index + 1)
                    else:
                        message = self._format_multiple_listings_for_run(new_listings, sub_index + 1)

                    self.send_message(chat_id, message)

                else:
                    message = f"<b>✅ Check Complete</b>\n\nNo <b>new</b> listings found for search #{sub_index + 1}.\n\nNote: Already seen {len(listings)} existing listings in this search."
                    self.send_message(chat_id, message)

                # Update last_checked timestamp
                self.database.update_last_checked(sub_id)

                return True

            except Exception as e:
                logger.error(f"[ERROR] Error fetching listings for /run: {e}")
                return self.send_message(chat_id, f"❌ Error checking search: {str(e)[:100]}")

        except ValueError:
            message = "❌ <b>Error:</b> Search number must be a number\n\n<i>Example: /run 1</i>"
            return self.send_message(chat_id, message)

        except Exception as e:
            logger.error(f"[ERROR] Error in /run command: {e}")
            return self.send_message(chat_id, "❌ An error occurred. Please try again.")

    def _handle_reset(self, chat_id: int, sub_number: str) -> bool:
        """
        Handle /reset command to clear seen listings for a specific subscription

        Args:
            chat_id: Telegram chat ID
            sub_number: Subscription number (1-based index) as string

        Returns:
            True if processed successfully
        """
        if not self.database:
            logger.error("[ERROR] Database not available")
            return self.send_message(chat_id, "❌ Database error. Please try again later.")

        if not sub_number:
            message = "❌ <b>Error:</b> Please specify which search to reset\n\n<i>/reset 1</i> - resets first search\n<i>/reset 2</i> - resets second search"
            return self.send_message(chat_id, message)

        try:
            # Get or create user for this chat_id
            user_id = self.database.get_or_create_telegram_user(chat_id)
            if not user_id:
                logger.error(f"[ERROR] Failed to get or create user for chat {chat_id}")
                return self.send_message(chat_id, "❌ Failed to retrieve user. Please try again later.")

            # Convert sub_number to integer (1-based index)
            sub_index = int(sub_number) - 1

            if sub_index < 0:
                message = "❌ <b>Error:</b> Search number must be 1 or higher"
                return self.send_message(chat_id, message)

            # Get subscriptions for this user
            subscriptions = self.database.get_subscriptions(user_id)

            if not subscriptions:
                message = "📋 You don't have any saved searches.\n\nUse /set to add a search."
                return self.send_message(chat_id, message)

            if sub_index >= len(subscriptions):
                message = f"❌ <b>Error:</b> You only have {len(subscriptions)} search(es).\n\nUse /list to see all searches."
                return self.send_message(chat_id, message)

            # Get the requested subscription
            subscription = subscriptions[sub_index]
            search_url = subscription.get("search_url")
            sub_id = subscription.get("id")

            logger.info(f"[*] Resetting seen listings for subscription {sub_id}: {search_url[:80]}")

            # Send "processing" status
            self.send_message(chat_id, "⏳ Resetting search memory... (this may take a moment)")

            # Create a fresh scraper instance for fetching listings
            if not self.config:
                logger.error("[ERROR] Configuration not available for /reset command")
                return self.send_message(chat_id, "❌ Search functionality not available. Please try again later.")

            try:
                # Import here to avoid circular imports
                from scraper import MyAutoScraper

                # Create fresh scraper instance (avoid threading/greenlet issues)
                scraper = MyAutoScraper(self.config)

                search_config = {
                    "base_url": search_url,
                    "parameters": {}
                }

                # Run scraper in thread pool to avoid Playwright asyncio conflicts
                # Playwright sync API doesn't work inside asyncio event loops,
                # so we run it in a separate thread with its own event loop context
                with ThreadPoolExecutor(max_workers=1) as executor:
                    listings = executor.submit(scraper.fetch_search_results, search_config).result(timeout=30)

                if not listings:
                    message = f"<b>✅ Reset Complete</b>\n\nSearch #{sub_index + 1} has no listings to reset.\n\nNote: The 'memory' is now clear - you'll see all listings on next check."
                    return self.send_message(chat_id, message)

                # Extract listing IDs
                listing_ids = [listing.get("listing_id") for listing in listings if listing.get("listing_id")]

                # Clear seen listings for these IDs
                cleared_count = self.database.clear_subscription_seen_listings_for_ids(user_id, listing_ids)

                if cleared_count > 0:
                    message = f"""<b>✅ Reset Complete!</b>

Search #{sub_index + 1} memory cleared!

🗑️ Cleared {cleared_count} tracked listings

Next time you use /run {sub_index + 1}, you'll see all {len(listings)} listings as "new"

<code>{search_url[:60]}...</code>"""
                    return self.send_message(chat_id, message)
                else:
                    message = f"""<b>✅ Reset Complete!</b>

Search #{sub_index + 1} already has no tracked listings.

This search has {len(listings)} total listings available.

<code>{search_url[:60]}...</code>"""
                    return self.send_message(chat_id, message)

            except Exception as e:
                logger.error(f"[ERROR] Error resetting subscription {sub_id}: {e}")
                return self.send_message(chat_id, f"❌ Error resetting search: {str(e)[:100]}")

        except ValueError:
            message = "❌ <b>Error:</b> Search number must be a number\n\n<i>Example: /reset 1</i>"
            return self.send_message(chat_id, message)

        except Exception as e:
            logger.error(f"[ERROR] Error in /reset command: {e}")
            return self.send_message(chat_id, "❌ An error occurred. Please try again.")

    @staticmethod
    def _format_single_listing_for_run(listing: Dict, search_num: int) -> str:
        """
        Format a single listing for /run command result
        Uses the same format as notifications_telegram.py for consistency

        Args:
            listing: Listing dictionary
            search_num: Search number (for context)

        Returns:
            Formatted message string
        """
        if not TelegramNotificationManager:
            # Fallback if notification manager not available
            return "Error: Cannot format listing"

        # Use the standard notification formatter
        message = TelegramNotificationManager._format_new_listing(listing)

        # Add search number info at the beginning
        message = f"<b>Search #{search_num}</b>\n\n" + message

        return message

    @staticmethod
    def _format_multiple_listings_for_run(listings: List[Dict], search_num: int) -> str:
        """
        Format multiple listings for /run command result
        Uses the same format as notifications_telegram.py for consistency

        Args:
            listings: List of listing dictionaries
            search_num: Search number (for context)

        Returns:
            Formatted message string or list of strings for batches
        """
        if not TelegramNotificationManager:
            # Fallback if notification manager not available
            return "Error: Cannot format listings"

        # Handle batching like the notification system does
        batches = TelegramNotificationManager._split_listings_into_batches(listings, max_listings_per_batch=10)

        if len(batches) == 1:
            # Single batch - use standard formatter
            message = TelegramNotificationManager._format_multiple_listings(batches[0])
        else:
            # Multiple batches - format with batch info
            message = TelegramNotificationManager._format_multiple_listings(
                batches[0],
                batch_num=1,
                total_batches=len(batches),
                total_listings=len(listings)
            )

        # Add search number info at the beginning
        message = f"<b>Search #{search_num}</b>\n\n" + message

        return message

    @staticmethod
    def _is_valid_myauto_url(url: str) -> bool:
        """
        Validate that URL is from MyAuto.ge

        Args:
            url: URL to validate

        Returns:
            True if valid MyAuto URL
        """
        if not url:
            return False

        # Check domain
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Accept both www and non-www versions
            if "myauto.ge" not in domain:
                return False

            # Check if it's a search URL (accept both /search and /s/ formats)
            path = parsed.path.lower()
            if "/search" not in path and "/s/" not in path:
                return False

            # URL must start with http or https
            if not url.startswith(("http://", "https://")):
                return False

            return True

        except Exception as e:
            logger.debug(f"[WARN] URL validation error: {e}")
            return False

    @staticmethod
    def _shorten_url(url: str, max_length: int = 50) -> str:
        """
        Shorten URL for display purposes

        Args:
            url: Full URL
            max_length: Maximum display length

        Returns:
            Shortened URL
        """
        if len(url) <= max_length:
            return url

        # Show start and end of URL
        half = (max_length - 3) // 2
        return f"{url[:half]}...{url[-half:]}"

    @staticmethod
    def _extract_search_details(url: str) -> str:
        """
        Extract readable search details from MyAuto URL

        Parses URL to show search criteria in human-readable format.
        Examples:
          - /ka/s/iyideba-motociklebi-ktm-690-smc → "KTM 690 SMC"
          - /ka/search?make=1&model=5 → "Search criteria"

        Args:
            url: MyAuto search URL

        Returns:
            Readable search description
        """
        try:
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(url)
            path = parsed.path.lower()

            # Try to extract from /s/ format (short URL with slug)
            # Format: /ka/s/iyideba-motociklebi-ktm-690-smc
            if "/s/" in path:
                parts = path.split("/s/")
                if len(parts) > 1:
                    slug = parts[-1]  # Get everything after /s/

                    # Remove query string from slug if present
                    if "?" in slug:
                        slug = slug.split("?")[0]

                    # Convert slug to readable format
                    # "iyideba-motociklebi-ktm-690-smc" → "KTM 690 SMC"
                    words = slug.split("-")

                    # Skip first few words which are usually category description
                    # ("iyideba" = "for sale", "motociklebi" = "motorcycles", etc.)
                    # Look for words that look like make/model (capitalized in slug)

                    readable_parts = []
                    for word in words:
                        # Skip common category words
                        if word.lower() in ['iyideba', 'motociklebi', 'avtomobilebi', 'gemi', 'ricxvi', 'da']:
                            continue
                        # Capitalize and add (removes hyphens within numbers like 690-smc)
                        if word:
                            readable_parts.append(word.upper() if len(word) <= 3 else word.capitalize())

                    if readable_parts:
                        details = " ".join(readable_parts)
                        return details[:50]  # Limit to 50 chars

            # Try to extract from query parameters in /search format
            query_params = parse_qs(parsed.query)

            details = []

            # Look for useful parameters
            if "make" in query_params:
                details.append(f"Make: {query_params['make'][0]}")
            if "model" in query_params:
                details.append(f"Model: {query_params['model'][0]}")
            if "priceFrom" in query_params or "priceTo" in query_params:
                price_from = query_params.get("priceFrom", [""])[0]
                price_to = query_params.get("priceTo", [""])[0]
                if price_from or price_to:
                    price_range = f"₾{price_from}" if price_from else ""
                    if price_to:
                        price_range += f"-{price_to}" if price_from else f"₾{price_to}"
                    if price_range:
                        details.append(price_range)

            if details:
                return " | ".join(details)[:50]

            # Default fallback
            return "MyAuto Search"

        except Exception as e:
            logger.debug(f"[WARN] Error extracting search details: {e}")
            return "Search"

    def run(self, poll_timeout: int = 30):
        """
        Main bot loop - continuously poll for updates and process messages

        Args:
            poll_timeout: Timeout for long polling in seconds
        """
        logger.info("[*] Starting Telegram Bot polling...")
        logger.info(f"[*] Bot token: {self.bot_token[:20]}...")

        poll_errors = 0
        max_consecutive_errors = 5

        try:
            while True:
                try:
                    # Get updates from Telegram
                    updates = self.get_updates(timeout=poll_timeout)

                    # Process each message
                    for update in updates:
                        if "message" in update:
                            self.process_message(update["message"])

                    # Reset error counter on successful poll
                    if updates or poll_errors > 0:
                        poll_errors = 0

                except KeyboardInterrupt:
                    logger.info("[*] Bot interrupted by user")
                    break

                except Exception as e:
                    poll_errors += 1
                    logger.error(f"[ERROR] Polling error ({poll_errors}/{max_consecutive_errors}): {e}")

                    if poll_errors >= max_consecutive_errors:
                        logger.error("[ERROR] Too many consecutive errors, stopping bot")
                        break

                    # Exponential backoff on errors
                    backoff_time = min(2 ** poll_errors, 60)
                    logger.info(f"[*] Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)

        except Exception as e:
            logger.error(f"[ERROR] Fatal error in bot loop: {e}")

        finally:
            logger.info("[*] Telegram Bot stopped")
