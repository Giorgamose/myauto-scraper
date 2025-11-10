#!/usr/bin/env python3
"""
Test the improved search results parsing
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from scraper import MyAutoScraper
from utils import load_config_file

# Load config
config = load_config_file('config.json')

# Create scraper
scraper = MyAutoScraper(config)

# Test with one search config
search_config = {
    'base_url': 'https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-land-cruiser-prado-1995-2008',
    'parameters': {}
}

print('[*] Fetching search results...')
results = scraper.fetch_search_results(search_config)
print(f'[OK] Found {len(results)} listings\n')

if results:
    for i, listing in enumerate(results[:10]):
        print(f"[{i+1}] {listing.get('title')} - ${listing.get('price')} | {listing.get('location')}")
else:
    print('[WARN] No listings found')
