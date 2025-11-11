#!/usr/bin/env python3
"""
User Management Module - Multi-User System
Handles user registration, authentication, and profile management
"""

import logging
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from urllib.parse import quote
import re

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

try:
    from database_rest_api import DatabaseManager
except ImportError as e:
    logger.error(f"[ERROR] Failed to import DatabaseManager: {e}")
    DatabaseManager = None


class UserManager:
    """Handle user registration, authentication, and profile management"""

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize UserManager with database connection

        Args:
            db_manager: DatabaseManager instance (creates new one if not provided)
        """
        if db_manager:
            self.db = db_manager
        elif DatabaseManager:
            self.db = DatabaseManager()
        else:
            logger.error("[ERROR] DatabaseManager not available")
            raise ImportError("Failed to import DatabaseManager")

        if self.db.connection_failed:
            logger.error("[ERROR] Failed to connect to Supabase")
            raise ConnectionError("Supabase connection failed")

        logger.info("[OK] User Manager initialized")

    # ========== PASSWORD HASHING ==========

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 + salt

        Args:
            password: Plain text password

        Returns:
            Hashed password with salt
        """
        # Generate random salt
        salt = secrets.token_hex(16)  # 32 character salt

        # Hash password with salt
        hash_obj = hashlib.sha256(f"{salt}{password}".encode())
        password_hash = hash_obj.hexdigest()

        # Combine salt and hash for storage
        return f"{salt}${password_hash}"

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        """
        Verify a password against stored hash

        Args:
            stored_hash: Hash stored in database
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        try:
            parts = stored_hash.split('$')
            if len(parts) != 2:
                return False

            salt, stored_password_hash = parts

            # Hash the provided password with the stored salt
            hash_obj = hashlib.sha256(f"{salt}{password}".encode())
            provided_hash = hash_obj.hexdigest()

            # Compare hashes
            return provided_hash == stored_password_hash
        except Exception as e:
            logger.error(f"[ERROR] Password verification failed: {e}")
            return False

    # ========== USER REGISTRATION ==========

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        telegram_chat_id: int = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Register a new user

        Args:
            username: Username (3-50 characters, alphanumeric + underscore)
            email: Email address
            password: Password (minimum 8 characters)
            first_name: Optional first name
            last_name: Optional last name
            telegram_chat_id: Optional Telegram chat ID

        Returns:
            Tuple of (success, error_message, user_data)
        """
        try:
            # Validate username
            if not username or len(username) < 3 or len(username) > 50:
                return False, "Username must be 3-50 characters", None

            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return False, "Username can only contain letters, numbers, and underscores", None

            # Validate email
            if not self._validate_email(email):
                return False, "Invalid email format", None

            # Validate password
            if not password or len(password) < 8:
                return False, "Password must be at least 8 characters", None

            # Check if username already exists
            existing_user = self._get_user_by_username(username)
            if existing_user:
                return False, "Username already exists", None

            # Check if email already exists
            existing_email = self._get_user_by_email(email)
            if existing_email:
                return False, "Email already registered", None

            # Check if telegram_chat_id already exists (if provided)
            if telegram_chat_id:
                existing_telegram = self._get_user_by_telegram_chat_id(telegram_chat_id)
                if existing_telegram:
                    return False, "Telegram chat ID already registered", None

            # Hash password
            password_hash = self.hash_password(password)

            # Prepare user data
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "first_name": first_name or None,
                "last_name": last_name or None,
                "telegram_chat_id": telegram_chat_id or None,
                "is_active": True,
                "is_verified": False,  # Email verification would happen here
                "notification_enabled": True,
                "check_interval_minutes": 15,
                "max_subscriptions": 50
            }

            # Insert user into database
            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/users",
                json=user_data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to register user: {response.status_code} - {response.text}")
                return False, "Registration failed", None

            # Get created user
            created_user = response.json() if isinstance(response.json(), dict) else response.json()[0]

            logger.info(f"[+] User registered: {username}")

            return True, None, {
                "id": created_user.get("id"),
                "username": username,
                "email": email,
                "telegram_chat_id": telegram_chat_id
            }

        except Exception as e:
            logger.error(f"[ERROR] Registration failed: {e}")
            return False, str(e), None

    # ========== USER AUTHENTICATION ==========

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate user with username and password

        Args:
            username: Username
            password: Password

        Returns:
            Tuple of (success, user_data or error_message)
        """
        try:
            # Get user by username
            user = self._get_user_by_username(username)
            if not user:
                return False, "Username or password incorrect"

            # Check if user is active
            if not user.get("is_active"):
                return False, "Account is disabled"

            # Verify password
            stored_hash = user.get("password_hash")
            if not self.verify_password(stored_hash, password):
                return False, "Username or password incorrect"

            # Update last login
            self._update_user_last_login(user.get("id"))

            logger.info(f"[+] User authenticated: {username}")

            return True, {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "telegram_chat_id": user.get("telegram_chat_id"),
                "notification_enabled": user.get("notification_enabled"),
                "check_interval_minutes": user.get("check_interval_minutes"),
                "max_subscriptions": user.get("max_subscriptions")
            }

        except Exception as e:
            logger.error(f"[ERROR] Authentication failed: {e}")
            return False, str(e)

    # ========== USER RETRIEVAL ==========

    def _get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            encoded_username = quote(username, safe='')
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/users?username=eq.{encoded_username}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user by username: {e}")
            return None

    def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            encoded_email = quote(email, safe='')
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/users?email=eq.{encoded_email}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user by email: {e}")
            return None

    def _get_user_by_telegram_chat_id(self, chat_id: int) -> Optional[Dict]:
        """Get user by Telegram chat ID"""
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/users?telegram_chat_id=eq.{chat_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user by telegram chat ID: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user ID"""
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/users?id=eq.{user_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user: {e}")
            return None

    # ========== API TOKEN MANAGEMENT ==========

    def create_api_token(self, user_id: str, token_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create API token for user

        Args:
            user_id: User ID
            token_name: Name for the token

        Returns:
            Tuple of (success, plain_token, token_id)
        """
        try:
            # Generate random token
            plain_token = secrets.token_urlsafe(32)

            # Hash token for storage
            token_hash = hashlib.sha256(plain_token.encode()).hexdigest()

            # Store in database
            token_data = {
                "user_id": user_id,
                "token_hash": token_hash,
                "token_name": token_name,
                "is_active": True
            }

            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/user_api_tokens",
                json=token_data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to create API token: {response.status_code}")
                return False, None, None

            token_record = response.json() if isinstance(response.json(), dict) else response.json()[0]
            token_id = token_record.get("id")

            logger.info(f"[+] API token created for user {user_id}: {token_name}")

            return True, plain_token, token_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to create API token: {e}")
            return False, None, None

    def verify_api_token(self, user_id: str, token: str) -> bool:
        """
        Verify API token for user

        Args:
            user_id: User ID
            token: Plain token provided by user

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Query for matching token
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_api_tokens?user_id=eq.{user_id}&token_hash=eq.{token_hash}&is_active=eq.true",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                tokens = response.json()
                if tokens:
                    token_record = tokens[0]

                    # Check if token has expiration
                    if token_record.get("expires_at"):
                        expires_at = datetime.fromisoformat(token_record.get("expires_at"))
                        if datetime.now(expires_at.tzinfo) > expires_at:
                            logger.warning(f"[!] API token expired for user {user_id}")
                            return False

                    # Update last_used_at
                    self.db._make_request(
                        'PATCH',
                        f"{self.db.base_url}/user_api_tokens?id=eq.{token_record.get('id')}",
                        json={"last_used_at": datetime.now().isoformat()},
                        headers=self.db.headers,
                        timeout=10
                    )

                    return True
            return False

        except Exception as e:
            logger.error(f"[ERROR] Failed to verify API token: {e}")
            return False

    # ========== USER UPDATES ==========

    def _update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/users?id=eq.{user_id}",
                json={"last_login": datetime.now().isoformat()},
                headers=self.db.headers,
                timeout=10
            )

            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"[ERROR] Failed to update last login: {e}")
            return False

    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Update user preferences

        Args:
            user_id: User ID
            preferences: Dictionary of preferences to update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Filter to only valid preference fields
            valid_fields = {
                "notification_enabled": bool,
                "check_interval_minutes": int,
                "max_subscriptions": int,
                "first_name": str,
                "last_name": str
            }

            update_data = {}
            for key, value in preferences.items():
                if key in valid_fields:
                    update_data[key] = value

            if not update_data:
                return True

            # Add update timestamp
            update_data["updated_at"] = datetime.now().isoformat()

            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/users?id=eq.{user_id}",
                json=update_data,
                headers=self.db.headers,
                timeout=10
            )

            return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"[ERROR] Failed to update user preferences: {e}")
            return False

    # ========== VALIDATION HELPERS ==========

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return re.match(email_pattern, email) is not None


# ============================================================================
# Test/Demo Functions
# ============================================================================

def test_user_management():
    """Test user management functionality"""
    try:
        manager = UserManager()

        # Test registration
        print("\n[*] Testing user registration...")
        success, error, user = manager.register_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User"
        )

        if success:
            print(f"[+] User registered: {user}")
            user_id = user.get("id")

            # Test authentication
            print("\n[*] Testing authentication...")
            auth_success, auth_result = manager.authenticate_user("testuser", "TestPassword123")
            if auth_success:
                print(f"[+] Authentication successful: {auth_result}")
            else:
                print(f"[-] Authentication failed: {auth_result}")

            # Test API token
            print("\n[*] Testing API token creation...")
            token_success, plain_token, token_id = manager.create_api_token(user_id, "test_token")
            if token_success:
                print(f"[+] API token created: {token_id}")
                print(f"[+] Token (save this): {plain_token}")

                # Test token verification
                print("\n[*] Testing token verification...")
                verify_success = manager.verify_api_token(user_id, plain_token)
                if verify_success:
                    print(f"[+] Token verification successful")
                else:
                    print(f"[-] Token verification failed")

        else:
            print(f"[-] Registration failed: {error}")

    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_user_management()
