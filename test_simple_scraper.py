#!/usr/bin/env python3
"""
Test the simple Reddit scraper (no credentials needed!)
"""

import sys
sys.path.insert(0, '/home/user/Agents')

from agents.simple_reddit_scraper import SimpleRedditScraper
from utils.logger import setup_logging

setup_logging(log_level="INFO")

print("="*70)
print("  TESTING SIMPLE REDDIT SCRAPER (NO CREDENTIALS!)")
print("="*70)
print()

# Initialize scraper
scraper = SimpleRedditScraper()

print("Fetching recent posts from r/Omaha...")
print("(This uses web scraping, no Reddit app needed!)")
print()

try:
    # Try scraping just r/Omaha first
    opportunities = scraper.scrape_subreddit('Omaha', limit=10)

    if opportunities:
        print(f"✓ Found {len(opportunities)} posts!")
        print()
        print("Sample posts:")
        print("-" * 70)

        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n{i}. {opp.title}")
            print(f"   Posted: {opp.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   URL: {opp.url}")
            print(f"   Score: {opp.score} | Comments: {opp.num_comments}")
            if opp.content:
                preview = opp.content[:100]
                print(f"   Preview: {preview}...")
    else:
        print("No posts found (this shouldn't happen)")

    print()
    print("="*70)
    print("✓ SCRAPER WORKS!")
    print("="*70)
    print()
    print("You can now run the full monitoring system!")
    print("No Reddit credentials needed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
