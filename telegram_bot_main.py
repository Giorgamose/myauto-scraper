#!/usr/bin/env python3
"""
Telegram Bot Main Entry Point
Run this script to start the Telegram bot backend with:
1. Command handling for /set, /list, /clear
2. Background scheduler for periodic new listing checks
3. Automatic notifications when new listings are found

Usage:
    python telegram_bot_main.py
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

# Setup logging before importing modules
from utils import setup_logging, get_log_level

log_level = get_log_level()
setup_logging(log_level)

logger = logging.getLogger(__name__)

# Import bot modules
try:
    from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser
    from telegram_bot_backend import TelegramBotBackend
    from telegram_bot_scheduler import TelegramBotScheduler
except ImportError as e:
    logger.error(f"[ERROR] Failed to import bot modules: {e}")
    sys.exit(1)

# Import existing project modules
try:
    from scraper import MyAutoScraper
    from notifications import NotificationManager
    from utils import load_config_file, get_config_path
except ImportError as e:
    logger.error(f"[ERROR] Failed to import project modules: {e}")
    sys.exit(1)


class TelegramBotApplication:
    """Main application for running the Telegram bot"""

    def __init__(self):
        """Initialize the bot application"""
        self.database = None
        self.bot_backend = None
        self.scheduler = None
        self.scraper = None
        self.notifier = None
        self.config = None

    def initialize(self) -> bool:
        """
        Initialize all components

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("[*] Initializing Telegram Bot Application...")

            # 1. Initialize database (uses existing Supabase instance - Multi-User)
            logger.info("[*] Initializing Supabase database (Multi-User System)...")
            try:
                self.database = TelegramBotDatabaseMultiUser()
                logger.info("[OK] Supabase database initialized (Multi-User)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize Supabase database: {e}")
                logger.error("[ERROR] Make sure:")
                logger.error("  1. SUPABASE_URL is set in .env.local")
                logger.error("  2. SUPABASE_API_KEY is set in .env.local")
                logger.error("  3. Database tables created (telegram_users, telegram_user_subscriptions, telegram_user_seen_listings, telegram_bot_events)")
                return False

            # 2. Load config for scraper (needed before initializing scraper)
            logger.info("[*] Loading configuration...")
            config_path = get_config_path()
            self.config = load_config_file(config_path)

            if not self.config:
                logger.error("[ERROR] Failed to load configuration")
                return False

            logger.info("[OK] Configuration loaded")

            # 3. Initialize scraper (for checking user subscriptions)
            logger.info("[*] Initializing scraper...")
            try:
                self.scraper = MyAutoScraper(self.config)
                logger.info("[OK] Scraper initialized")
            except Exception as e:
                logger.warning(f"[WARN] Failed to initialize scraper: {e}")
                logger.info("[*] Scraper will be attempted again during scheduler checks")

            # 4. Initialize bot backend (now with scraper for /run command)
            logger.info("[*] Initializing bot backend...")
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                logger.error("[ERROR] TELEGRAM_BOT_TOKEN not found in environment")
                return False

            self.bot_backend = TelegramBotBackend(
                bot_token=bot_token,
                database=self.database,
                scraper=self.scraper,
                config=self.config  # Pass config so /run can create fresh scraper instances
            )

            # Set allowed chats if configured
            allowed_chats_str = os.getenv("BOT_ALLOWED_CHATS", "").strip()
            if allowed_chats_str:
                try:
                    allowed_chats = [int(cid.strip()) for cid in allowed_chats_str.split(",")]
                    self.bot_backend.set_allowed_chats(allowed_chats)
                except ValueError:
                    logger.warning("[WARN] Invalid BOT_ALLOWED_CHATS format, allowing all chats")

            logger.info("[OK] Bot backend initialized")

            # 5. Initialize notifications (for sending new listing alerts)
            logger.info("[*] Initializing notifications...")
            try:
                self.notifier = NotificationManager()
                if self.notifier.is_ready():
                    logger.info("[OK] Notifications initialized")
                else:
                    logger.warning("[WARN] Notifications not fully configured")
            except Exception as e:
                logger.warning(f"[WARN] Failed to initialize notifications: {e}")

            # 6. Initialize scheduler (background check loop)
            logger.info("[*] Initializing scheduler...")
            check_interval = int(os.getenv("BOT_CHECK_INTERVAL_MINUTES", "15"))

            self.scheduler = TelegramBotScheduler(
                database=self.database,
                bot_backend=self.bot_backend,
                config=self.config,  # Pass config so scheduler creates its own scraper in its thread
                notifications_manager=self.notifier,
                check_interval_minutes=check_interval,
                daemon=False  # Not a daemon so we can control shutdown
            )

            logger.info(f"[OK] Scheduler initialized (check interval: {check_interval} minutes)")

            logger.info("[OK] All components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Initialization failed: {e}")
            return False

    def run(self):
        """
        Main application loop

        Runs:
        1. Bot backend (polls for Telegram messages and processes commands)
        2. Scheduler (periodically checks subscriptions for new listings)
        """
        try:
            if not self.initialize():
                logger.error("[ERROR] Failed to initialize application")
                return False

            logger.info("=" * 60)
            logger.info("[*] Starting Telegram Bot Application")
            logger.info("=" * 60)

            # Log bot info
            logger.info("[*] Bot features:")
            logger.info("  ✓ /set <url>  - Add a MyAuto search to monitor")
            logger.info("  ✓ /list       - Show your saved searches")
            logger.info("  ✓ /run <num>  - Immediately check a saved search")
            logger.info("  ✓ /reset <num> - Clear tracking history for a search")
            logger.info("  ✓ /clear      - Remove all saved searches")
            logger.info("  ✓ /status     - Show bot statistics")
            logger.info("  ✓ /help       - Show help message")

            # Start scheduler in background thread
            logger.info("[*] Starting background scheduler...")
            self.scheduler.start()
            logger.info("[OK] Scheduler started")

            # Run bot backend (blocking call)
            logger.info("[*] Starting bot message handler (long polling)...")
            logger.info("[*] Bot is now listening for messages...")
            self.bot_backend.run(poll_timeout=30)

        except KeyboardInterrupt:
            logger.info("[*] Application interrupted by user")

        except Exception as e:
            logger.error(f"[ERROR] Fatal error in application: {e}")
            return False

        finally:
            self.shutdown()

        return True

    def shutdown(self):
        """Graceful shutdown of all components"""
        try:
            logger.info("[*] Shutting down application...")

            # Stop scheduler
            if self.scheduler:
                logger.info("[*] Stopping scheduler...")
                self.scheduler.stop()
                # Wait for scheduler to finish
                self.scheduler.join(timeout=5)
                logger.info("[OK] Scheduler stopped")

            # Database cleanup (Supabase doesn't need explicit close)
            if self.database:
                logger.info("[*] Supabase connection closed")

            logger.info("=" * 60)
            logger.info("[OK] Application shutdown complete")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"[ERROR] Error during shutdown: {e}")


def main():
    """Main entry point"""
    try:
        logger.info("[*] MyAuto Telegram Bot Backend")
        logger.info("[*] Version: 1.0.0")

        # Create and run application
        app = TelegramBotApplication()
        success = app.run()

        # Exit with appropriate code
        exit_code = 0 if success else 1
        logger.info(f"[*] Exiting with code {exit_code}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("[*] Interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
