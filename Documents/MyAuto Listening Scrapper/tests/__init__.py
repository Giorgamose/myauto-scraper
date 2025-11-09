"""
MyAuto Car Listing Scraper - Test Suite

This directory contains all test files for the MyAuto scraper system.

Test Files:
  - test_integration.py - Complete integration test of all components
  - test_telegram.py - Telegram Bot API connectivity test
  - test_turso.py - Turso database connectivity test
  - test_turso_sync.py - Synchronous Turso client test
  - test_turso_async.py - Asynchronous Turso client test
  - test_turso_simple.py - Simple Turso connection test
  - run_test_telegram.py - Clean test runner with cache clearing

Usage:
  # Run all integration tests
  python -m pytest tests/

  # Run specific test
  python tests/test_integration.py

  # Run with clean cache
  python tests/run_test_telegram.py
"""
