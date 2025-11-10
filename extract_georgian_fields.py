#!/usr/bin/env python3
"""
Extract all vehicle fields using Georgian labels
Maps Georgian labels to database fields
"""

from bs4 import BeautifulSoup
import re
import json
import sys
import os

# Fix encoding for Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Georgian to English field mapping
GEORGIAN_FIELD_MAP = {
    'მწარმოებელი': ('make', str),
    'მოდელი': ('model', str),
    'წელი': ('year', int),
    'კატეგორია': ('category', str),
    'გარბენი': ('mileage_km', lambda x: int(re.sub(r'[^\d]', '', x)) if x else None),
    'საწვავის ტიპი': ('fuel_type', str),
    'ძრავის მოცულობა': ('displacement_liters', float),
    'ცილინდრები': ('cylinders', int),
    'გადაცემათა კოლოფი': ('transmission', str),
    'წამყვანი თვლები': ('drive_type', str),
    'კარები': ('doors', lambda x: int(re.search(r'\d+', str(x)).group()) if x else None),
    'აირბეგი': ('seats', int),
    'საჭე': ('wheel_position', str),
    'ფერი': ('color', str),
    'სალონის ფერი': ('interior_color', str),
    'სალონის მასალა': ('interior_material', str),
    'ფასი': ('price', lambda x: int(re.sub(r'[^\d]', '', str(x))) if x else None),
    'განბაჟება': ('customs_cleared', lambda x: 1 if x and 'გ' in x else 0),  # Georgian 'გ' = yes
    'ტექ. დათვალიერება': ('technical_inspection', lambda x: 1 if x and 'კ' in x else 0),  # 'კ' = yes
    'კატალიზატორი': ('has_catalytic_converter', lambda x: 1 if x and 'კ' in x else 0),
    'გაცვლა': ('exchange_possible', lambda x: 1 if x and 'კ' in x else 0),
}

def extract_fields_from_html(html):
    """
    Extract all fields from HTML using Georgian labels
    """
    soup = BeautifulSoup(html, "lxml")
    all_text = soup.get_text()

    extracted = {}

    # For each Georgian label, search for it and extract the value
    for georgian, (field_name, converter) in GEORGIAN_FIELD_MAP.items():
        try:
            # Find the label in the text
            if georgian not in all_text:
                continue

            # Find the element containing the label
            elements = soup.find_all(lambda tag: tag.string and georgian in tag.string)

            if not elements:
                continue

            elem = elements[0]

            # Get the parent element
            parent = elem.parent
            while parent and parent.name in ['span', 'div'] and len(parent.find_all()) < 5:
                parent = parent.parent

            # Extract text from parent (exclude the label itself)
            full_text = parent.get_text(strip=True) if parent else ""

            # Try to get just the value part (after the colon or label)
            if ':' in full_text:
                value = full_text.split(':', 1)[1].strip()
            else:
                # Remove the label from the text
                value = full_text.replace(georgian, '').strip()

            # Clean up the value
            value = value.split()[0] if value.split() else None

            # Convert if needed
            if value and converter:
                try:
                    converted = converter(value)
                    extracted[field_name] = converted
                    print(f"  [OK] {field_name}: {converted}")
                except Exception as e:
                    print(f"  [!] {field_name}: conversion failed ({value}) - {e}")
                    # Store as string
                    extracted[field_name] = value
            else:
                extracted[field_name] = value

        except Exception as e:
            print(f"  [!] Error extracting: {e}")
            continue

    return extracted


# Test it
if __name__ == "__main__":
    print("[*] Reading HTML...\n")
    with open("debug_listing.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("[*] Extracting Georgian fields...\n")
    fields = extract_fields_from_html(html)

    print(f"\n[*] Extracted {len(fields)} fields:")
    for field, value in sorted(fields.items()):
        print(f"    {field}: {value} ({type(value).__name__})")

    print(f"\n[*] JSON output:")
    print(json.dumps(fields, indent=2, default=str, ensure_ascii=False))
