#!/usr/bin/env python3
"""
Clean Telegram Test Runner
Run this if you get SSL errors with test_telegram.py
"""

import subprocess
import sys
import os

print("\n" + "="*70)
print("TELEGRAM TEST RUNNER - FRESH START")
print("="*70 + "\n")

# Step 1: Check Python version
print("[*] Step 1: Checking Python version...")
python_version = sys.version
print(f"[OK] Python: {python_version.split()[0]}")

# Step 2: Check urllib3 is installed
print("\n[*] Step 2: Checking urllib3...")
try:
    import urllib3
    print("[OK] urllib3 is installed")
except ImportError:
    print("[ERROR] urllib3 not installed, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "urllib3", "-q"])
    print("[OK] urllib3 installed")

# Step 3: Check requests is installed
print("\n[*] Step 3: Checking requests...")
try:
    import requests
    print("[OK] requests is installed")
except ImportError:
    print("[ERROR] requests not installed, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    print("[OK] requests installed")

# Step 4: Clear Python cache
print("\n[*] Step 4: Clearing Python cache...")
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        import shutil
        shutil.rmtree(os.path.join(root, "__pycache__"))
print("[OK] Cache cleared")

# Step 5: Run the actual test
print("\n[*] Step 5: Running test_telegram.py...\n")
print("="*70 + "\n")

try:
    result = subprocess.run(
        [sys.executable, "test_telegram.py"],
        timeout=60
    )
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print("\n[ERROR] Test timed out")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)
