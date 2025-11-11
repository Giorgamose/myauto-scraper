#!/usr/bin/env python3
"""
Search Criteria Management Module - Multi-User System
Allows users to create, edit, and manage their own search criteria
Replaces hardcoded config.json approach
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from urllib.parse import quote
import json

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

logger = logging.getLogger(__name__)

try:
    from database_rest_api import DatabaseManager
except ImportError as e:
    logger.error(f"[ERROR] Failed to import DatabaseManager: {e}")
    DatabaseManager = None


class SearchCriteriaManager:
    """Manage user-specific search criteria"""

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize SearchCriteriaManager

        Args:
            db_manager: DatabaseManager instance
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

        logger.info("[OK] Search Criteria Manager initialized")

    # ========== SEARCH CRITERIA CRUD ==========

    def create_criteria(
        self,
        user_id: str,
        criteria_name: str,
        search_parameters: Dict,
        description: str = None,
        notification_enabled: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Create new search criteria for user

        Args:
            user_id: User ID
            criteria_name: Name for the criteria
            search_parameters: Dictionary of search parameters (see example below)
            description: Optional description
            notification_enabled: Whether to send notifications for this criteria

        Returns:
            Tuple of (success, error_message, criteria_data)

        Example search_parameters:
        {
            "vehicleType": 0,
            "makes": [1, 2, 3],
            "models": [10, 11, 12],
            "priceFrom": 5000,
            "priceTo": 50000,
            "yearFrom": 2000,
            "yearTo": 2024,
            "fuelTypes": [1, 2, 3],
            "transmission": [1, 2],
            "mileageFrom": 0,
            "mileageTo": 500000,
            "customs": 1,
            "locations": [1, 2, 3],
            "engineVolumeFrom": 0,
            "engineVolumeTo": 8000
        }
        """
        try:
            # Validate criteria name
            if not criteria_name or len(criteria_name) < 3 or len(criteria_name) > 100:
                return False, "Criteria name must be 3-100 characters", None

            # Check for duplicate criteria name for this user
            existing = self._get_criteria_by_name(user_id, criteria_name)
            if existing:
                return False, f"Criteria '{criteria_name}' already exists for this user", None

            # Validate search parameters
            if not isinstance(search_parameters, dict):
                return False, "Search parameters must be a dictionary", None

            # Prepare data
            criteria_data = {
                "user_id": user_id,
                "criteria_name": criteria_name,
                "description": description or None,
                "search_parameters": search_parameters,
                "notification_enabled": notification_enabled,
                "is_active": True
            }

            # Insert into database
            response = self.db._make_request(
                'POST',
                f"{self.db.base_url}/user_search_criteria",
                json=criteria_data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code not in [200, 201]:
                logger.error(f"[ERROR] Failed to create criteria: {response.status_code} - {response.text}")
                return False, "Failed to create criteria", None

            created_criteria = response.json() if isinstance(response.json(), dict) else response.json()[0]

            logger.info(f"[+] Search criteria created for user {user_id}: {criteria_name}")

            return True, None, {
                "id": created_criteria.get("id"),
                "criteria_name": criteria_name,
                "description": description,
                "search_parameters": search_parameters
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to create criteria: {e}")
            return False, str(e), None

    def get_user_criteria(self, user_id: str, include_inactive: bool = False) -> List[Dict]:
        """
        Get all criteria for a user

        Args:
            user_id: User ID
            include_inactive: Whether to include inactive criteria

        Returns:
            List of criteria dictionaries
        """
        try:
            filter_str = f"user_id=eq.{user_id}"
            if not include_inactive:
                filter_str += "&is_active=eq.true"

            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_search_criteria?{filter_str}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception as e:
            logger.error(f"[ERROR] Failed to get user criteria: {e}")
            return []

    def get_criteria_by_id(self, criteria_id: str, user_id: str = None) -> Optional[Dict]:
        """
        Get specific criteria

        Args:
            criteria_id: Criteria ID
            user_id: Optional user ID for authorization check

        Returns:
            Criteria dictionary or None
        """
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_search_criteria?id=eq.{criteria_id}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                criteria_list = response.json()
                if criteria_list:
                    criteria = criteria_list[0]

                    # Check authorization if user_id provided
                    if user_id and criteria.get("user_id") != user_id:
                        logger.warning(f"[!] Unauthorized access to criteria {criteria_id}")
                        return None

                    return criteria
            return None

        except Exception as e:
            logger.error(f"[ERROR] Failed to get criteria: {e}")
            return None

    def update_criteria(
        self,
        criteria_id: str,
        user_id: str,
        updates: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Update search criteria

        Args:
            criteria_id: Criteria ID
            user_id: User ID (for authorization)
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Verify ownership
            criteria = self.get_criteria_by_id(criteria_id, user_id)
            if not criteria:
                return False, "Criteria not found or unauthorized"

            # Validate updatable fields
            updatable_fields = {
                "criteria_name", "description", "search_parameters",
                "notification_enabled", "is_active"
            }

            update_data = {}
            for key, value in updates.items():
                if key in updatable_fields:
                    update_data[key] = value

            if not update_data:
                return True, None

            # Add update timestamp
            update_data["updated_at"] = datetime.now().isoformat()

            response = self.db._make_request(
                'PATCH',
                f"{self.db.base_url}/user_search_criteria?id=eq.{criteria_id}",
                json=update_data,
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"[+] Criteria updated: {criteria_id}")
                return True, None
            else:
                logger.error(f"[ERROR] Failed to update criteria: {response.status_code}")
                return False, "Update failed"

        except Exception as e:
            logger.error(f"[ERROR] Failed to update criteria: {e}")
            return False, str(e)

    def delete_criteria(self, criteria_id: str, user_id: str, soft_delete: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Delete search criteria (soft or hard delete)

        Args:
            criteria_id: Criteria ID
            user_id: User ID (for authorization)
            soft_delete: If True, mark as inactive. If False, hard delete.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Verify ownership
            criteria = self.get_criteria_by_id(criteria_id, user_id)
            if not criteria:
                return False, "Criteria not found or unauthorized"

            if soft_delete:
                # Mark as inactive
                response = self.db._make_request(
                    'PATCH',
                    f"{self.db.base_url}/user_search_criteria?id=eq.{criteria_id}",
                    json={"is_active": False},
                    headers=self.db.headers,
                    timeout=10
                )
            else:
                # Hard delete
                response = self.db._make_request(
                    'DELETE',
                    f"{self.db.base_url}/user_search_criteria?id=eq.{criteria_id}",
                    headers=self.db.headers,
                    timeout=10
                )

            if response.status_code in [200, 204]:
                logger.info(f"[+] Criteria deleted: {criteria_id}")
                return True, None
            else:
                logger.error(f"[ERROR] Failed to delete criteria: {response.status_code}")
                return False, "Delete failed"

        except Exception as e:
            logger.error(f"[ERROR] Failed to delete criteria: {e}")
            return False, str(e)

    # ========== HELPERS ==========

    def _get_criteria_by_name(self, user_id: str, criteria_name: str) -> Optional[Dict]:
        """Get criteria by name for a user"""
        try:
            encoded_name = quote(criteria_name, safe='')
            response = self.db._make_request(
                'GET',
                f"{self.db.base_url}/user_search_criteria?user_id=eq.{user_id}&criteria_name=eq.{encoded_name}",
                headers=self.db.headers,
                timeout=10
            )

            if response.status_code == 200:
                criteria_list = response.json()
                return criteria_list[0] if criteria_list else None
            return None

        except Exception as e:
            logger.error(f"[ERROR] Failed to get criteria by name: {e}")
            return None

    def validate_search_parameters(self, params: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate search parameters structure

        Args:
            params: Search parameters dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Define valid parameter types
        valid_params = {
            "vehicleType": (int, type(None)),
            "makes": (list, type(None)),
            "models": (list, type(None)),
            "priceFrom": (int, float, type(None)),
            "priceTo": (int, float, type(None)),
            "yearFrom": (int, type(None)),
            "yearTo": (int, type(None)),
            "fuelTypes": (list, type(None)),
            "transmission": (list, type(None)),
            "mileageFrom": (int, float, type(None)),
            "mileageTo": (int, float, type(None)),
            "customs": (int, type(None)),
            "locations": (list, type(None)),
            "engineVolumeFrom": (int, float, type(None)),
            "engineVolumeTo": (int, float, type(None)),
            "seatCount": (int, type(None)),
            "doorsCount": (int, type(None)),
            "colorId": (int, type(None)),
        }

        for key, value in params.items():
            if key not in valid_params:
                return False, f"Unknown parameter: {key}"

            expected_types = valid_params[key]
            if not isinstance(value, expected_types):
                return False, f"Invalid type for {key}: expected {expected_types}, got {type(value)}"

        return True, None

    # ========== EXPORT/IMPORT ==========

    def export_criteria_to_dict(self, criteria_id: str, user_id: str) -> Optional[Dict]:
        """
        Export criteria as dictionary (for backup/sharing)

        Args:
            criteria_id: Criteria ID
            user_id: User ID

        Returns:
            Criteria dictionary or None
        """
        criteria = self.get_criteria_by_id(criteria_id, user_id)
        if criteria:
            return {
                "criteria_name": criteria.get("criteria_name"),
                "description": criteria.get("description"),
                "search_parameters": criteria.get("search_parameters"),
                "notification_enabled": criteria.get("notification_enabled")
            }
        return None

    def import_criteria_from_dict(
        self,
        user_id: str,
        data: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Import criteria from dictionary

        Args:
            user_id: User ID
            data: Dictionary with criteria_name, search_parameters, etc.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            criteria_name = data.get("criteria_name")
            search_parameters = data.get("search_parameters")
            description = data.get("description")
            notification_enabled = data.get("notification_enabled", True)

            if not criteria_name or not search_parameters:
                return False, "criteria_name and search_parameters required"

            # Validate parameters
            valid, error = self.validate_search_parameters(search_parameters)
            if not valid:
                return False, error

            # Create criteria
            success, error, _ = self.create_criteria(
                user_id=user_id,
                criteria_name=criteria_name,
                search_parameters=search_parameters,
                description=description,
                notification_enabled=notification_enabled
            )

            return success, error

        except Exception as e:
            logger.error(f"[ERROR] Failed to import criteria: {e}")
            return False, str(e)


# ============================================================================
# Example Search Criteria Presets
# ============================================================================

SEARCH_CRITERIA_PRESETS = {
    "luxury_suv": {
        "criteria_name": "Luxury SUVs (Recent)",
        "description": "Recent luxury SUVs under 100K",
        "search_parameters": {
            "vehicleType": 1,  # SUV
            "makes": [1, 2, 3],  # Example: Mercedes, BMW, Audi
            "priceFrom": 30000,
            "priceTo": 100000,
            "yearFrom": 2015,
            "yearTo": 2024,
            "customs": 1  # Customs cleared
        }
    },
    "budget_sedan": {
        "criteria_name": "Budget Sedans (Reliable)",
        "description": "Affordable, reliable sedans",
        "search_parameters": {
            "vehicleType": 0,  # Sedan
            "priceFrom": 5000,
            "priceTo": 15000,
            "yearFrom": 2010,
            "yearTo": 2020,
            "mileageFrom": 0,
            "mileageTo": 200000
        }
    },
    "eco_hatchback": {
        "criteria_name": "Eco-Friendly Hatchbacks",
        "description": "Fuel-efficient hatchbacks",
        "search_parameters": {
            "vehicleType": 2,  # Hatchback
            "fuelTypes": [3],  # Hybrid/Electric
            "priceFrom": 10000,
            "priceTo": 40000,
            "yearFrom": 2018,
            "yearTo": 2024
        }
    }
}


# ============================================================================
# Test/Demo Functions
# ============================================================================

def test_search_criteria_management():
    """Test search criteria management functionality"""
    try:
        manager = SearchCriteriaManager()

        # For testing, use a known user_id
        test_user_id = "test-user-123"

        # Test creating criteria
        print("\n[*] Testing criteria creation...")
        success, error, criteria = manager.create_criteria(
            user_id=test_user_id,
            criteria_name="Test Criteria",
            search_parameters={
                "vehicleType": 0,
                "priceFrom": 5000,
                "priceTo": 50000,
                "yearFrom": 2015,
                "yearTo": 2024
            },
            description="Test search criteria"
        )

        if success:
            print(f"[+] Criteria created: {criteria}")
            criteria_id = criteria.get("id")

            # Test getting criteria
            print("\n[*] Testing get criteria...")
            retrieved = manager.get_criteria_by_id(criteria_id, test_user_id)
            if retrieved:
                print(f"[+] Criteria retrieved: {retrieved.get('criteria_name')}")

            # Test updating criteria
            print("\n[*] Testing criteria update...")
            update_success, update_error = manager.update_criteria(
                criteria_id=criteria_id,
                user_id=test_user_id,
                updates={
                    "description": "Updated test criteria",
                    "notification_enabled": False
                }
            )

            if update_success:
                print(f"[+] Criteria updated successfully")

        else:
            print(f"[-] Creation failed: {error}")

        # Test listing user criteria
        print("\n[*] Testing get user criteria...")
        user_criteria = manager.get_user_criteria(test_user_id)
        print(f"[+] Found {len(user_criteria)} criteria for user")

    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_search_criteria_management()
