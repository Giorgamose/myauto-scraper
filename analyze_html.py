#!/usr/bin/env python3
"""
Analyze the saved HTML to understand structure
"""

from bs4 import BeautifulSoup
import re
import json
import sys

# Fix encoding for Windows console
import os
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

print("[*] Reading debug_listing.html...")
with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

print(f"[*] HTML Size: {len(html)} bytes")

# Check title
try:
    title_text = soup.title.string if soup.title else "None"
    print(f"[*] Title present: {bool(soup.title)}")
except:
    print("[*] Title: (error reading)")

print(f"\n[*] Looking for JSON in script tags...")
scripts = soup.find_all("script")
found_data = False

for i, script in enumerate(scripts):
    if not script.string:
        continue

    content = script.string

    # Check if it contains keywords
    if any(keyword in content.lower() for keyword in ["listing", "vehicle", "make", "model", "price", "mileage"]):
        print(f"\n    Script [{i}] - {len(content)} chars:")
        found_data = True

        # Try to find JSON in the content
        try:
            # Try direct JSON parse
            data = json.loads(content)
            print(f"      ✓ Valid JSON, keys: {list(data.keys())[:5]}")

            # Look for vehicle data
            def search_dict(d, depth=0):
                if isinstance(d, dict):
                    for k, v in d.items():
                        if k in ["listing", "vehicle", "make", "model", "year", "price", "mileage"]:
                            print(f"        Found '{k}': {type(v).__name__}")
                        if isinstance(v, (dict, list)):
                            search_dict(v, depth+1)
                elif isinstance(d, list) and len(d) > 0:
                    search_dict(d[0], depth+1)

            search_dict(data)
        except Exception as e:
            # Look for JSON-like patterns
            matches = re.findall(r'"(make|model|year|price|mileage|listing)"', content)
            if matches:
                print(f"      Found keywords: {set(matches)}")

if not found_data:
    print("    No scripts with vehicle keywords found")

print(f"\n[*] Looking for vehicle-related HTML elements...")

# Look for elements containing text like "Toyota", "Land Cruiser", etc
elements = soup.find_all(True)  # All elements
vehicle_elements = []
for elem in elements:
    text = elem.get_text() if elem.string is None else str(elem.string)
    if any(keyword in text for keyword in ["Toyota", "Cruiser", "Honda", "BMW", "Mercedes"]):
        vehicle_elements.append((elem.name, elem.attrs, text[:80]))

print(f"Found {len(vehicle_elements)} elements with vehicle keywords")
for i, (tag, attrs, text) in enumerate(vehicle_elements[:10]):
    print(f"  [{i}] <{tag}> with {len(attrs)} attributes")

print(f"\n[*] Checking page content structure...")
# Count different element types
tags = [elem.name for elem in soup.find_all()]
from collections import Counter
tag_counts = Counter(tags)
print(f"Most common tags: {tag_counts.most_common(10)}")

print(f"\n[OK] Analysis complete!")
