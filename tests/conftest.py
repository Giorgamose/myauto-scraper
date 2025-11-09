"""
Pytest Configuration for MyAuto Tests

This file configures the test environment and provides fixtures for testing.
"""

import sys
import os

# Add parent directory to Python path so tests can import application modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture
def config_path():
    """Fixture providing path to config.json"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')


@pytest.fixture
def project_root():
    """Fixture providing the root project directory"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def test_telegram_credentials():
    """Fixture providing test Telegram credentials"""
    return {
        'bot_token': '8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4',
        'chat_id': '6366712840'
    }
