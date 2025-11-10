#!/usr/bin/env python3
"""
Extract ALL available fields from vehicle detail page HTML
"""

from bs4 import BeautifulSoup
import sys
import os
import re
import json

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

print("[*] Reading saved HTML...")
with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Extract all text and organize by element
print("[*] Extracting all visible text by section...\n")

# Get body content
body = soup.body if soup.body else soup

# Find all text nodes with their parent elements
sections = {}

for elem in body.find_all(True):  # All elements
    text = elem.get_text(strip=True)

    if not text or len(text) < 3:
        continue

    # Skip script and style tags
    if elem.name in ['script', 'style']:
        continue

    # Get parent class for context
    parent_class = ' '.join(elem.get('class', []))
    section_key = f"{elem.name}:{parent_class[:50]}"

    if section_key not in sections:
        sections[section_key] = []

    sections[section_key].append(text[:100])

# Print organized sections
for section, texts in sorted(sections.items())[:30]:
    if texts:
        print(f"\n[{section}]")
        for text in texts[:3]:
            print(f"  - {text}")

# Look for spec/property patterns
print(f"\n{'='*70}")
print("[*] Looking for specification/property patterns...")
print(f"{'='*70}\n")

# Find divs that might contain key-value pairs
divs = soup.find_all('div')
specs_found = []

for div in divs:
    text = div.get_text(strip=True)

    # Look for patterns like "Property: Value"
    if ':' in text and len(text) > 10 and len(text) < 200:
        specs_found.append(text)

# Deduplicate and print
for spec in sorted(set(specs_found)):
    if any(keyword in spec.lower() for keyword in ['year', 'price', 'mileage', 'fuel', 'transmission', 'make', 'model', 'color', 'body', 'km', 'usd', 'gel']):
        print(f"  {spec[:150]}")

# Look for structured data
print(f"\n{'='*70}")
print("[*] Looking for all visible field labels and values...")
print(f"{'='*70}\n")

# Search for any element that might contain "Price", "Year", "Mileage", etc
labels = ['Price', 'Mileage', 'Year', 'Make', 'Model', 'Fuel', 'Transmission',
          'Color', 'Body Type', 'Power', 'Engine', 'Doors', 'Seats', 'Registration',
          'Customs', 'Inspection', 'VIN', 'Location', 'Seller', 'Phone', 'Posted',
          'Updated', 'Status', 'Condition', 'Category', 'Type', 'Class']

found_labels = {}
for label in labels:
    elements = soup.find_all(lambda tag: tag.string and label in tag.string, limit=5)
    if elements:
        found_labels[label] = []
        for elem in elements:
            # Get neighboring text
            parent = elem.parent
            sibling_text = ''.join([s.get_text(strip=True) for s in parent.find_all(recursive=False)])[:100]
            found_labels[label].append({
                'element': elem.name,
                'text': elem.string[:50],
                'parent_class': ' '.join(parent.get('class', [])),
                'siblings': sibling_text
            })

for label, findings in found_labels.items():
    print(f"\n[{label}]")
    for finding in findings[:2]:
        print(f"  Element: <{finding['element']}>")
        print(f"  Text: {finding['text']}")
        print(f"  Class: {finding['parent_class'][:60]}")

# Check for lists or property items
print(f"\n{'='*70}")
print("[*] Looking for list items or property cards...")
print(f"{'='*70}\n")

# Find list items that might contain properties
lists = soup.find_all(['ul', 'li'])
print(f"Found {len(lists)} list elements")

for list_elem in lists[:10]:
    text = list_elem.get_text(strip=True)[:150]
    if text:
        print(f"  <{list_elem.name}> {text}")

# Check for all text in specific containers
print(f"\n{'='*70}")
print("[*] Full page structure summary...")
print(f"{'='*70}\n")

all_text = soup.get_text()
print(f"Total text length: {len(all_text)} characters")
print(f"Total elements: {len(list(soup.find_all()))}")

# Count element types
from collections import Counter
tag_counts = Counter([elem.name for elem in soup.find_all()])
print(f"\nMost common elements:")
for tag, count in tag_counts.most_common(15):
    if tag not in ['path', 'image', 'g']:
        print(f"  {tag}: {count}")
