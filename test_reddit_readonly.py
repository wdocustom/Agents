#!/usr/bin/env python3
"""
Quick test script to try Reddit monitoring WITHOUT credentials.
"""

import sys
sys.path.insert(0, '/home/user/Agents')

from agents.reddit_monitor_readonly import RedditMonitorReadOnly
from utils.logger import setup_logging

setup_logging(log_level="INFO")

print("="*70)
print("  TESTING REDDIT READ-ONLY MODE (NO CREDENTIALS NEEDED)")
print("="*70)
print()

# Try to initialize
monitor = RedditMonitorReadOnly()

if not monitor.authenticated:
    print("✗ Failed to initialize Reddit")
    print("\nThis method may not work anymore. You'll need to:")
    print("1. Go to https://old.reddit.com/prefs/apps")
    print("2. Create a 'script' app")
    print("3. Add credentials to .env file")
    sys.exit(1)

print("✓ Reddit initialized in read-only mode")
print()

# Try to get posts from r/Omaha
print("Fetching recent posts from r/Omaha...")
try:
    opportunities = monitor.monitor_new_posts(hours_back=48, limit=25)

    print(f"\n✓ Found {len(opportunities)} posts from the last 48 hours")
    print()

    if opportunities:
        print("Sample posts:")
        print("-" * 70)
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n{i}. {opp.title}")
            print(f"   Posted {opp.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   URL: {opp.url}")
            if opp.content:
                print(f"   Preview: {opp.content[:100]}...")
    else:
        print("No posts found in that timeframe")

except Exception as e:
    print(f"✗ Error: {e}")
    print("\nRead-only mode doesn't work. You need to create a Reddit app.")
    sys.exit(1)

print()
print("="*70)
print("✓ READ-ONLY MODE WORKS!")
print("="*70)
print()
print("You can monitor Reddit without credentials!")
print("However, you CANNOT post comments without full authentication.")
print()
print("For monitoring only, this works fine.")
print("For auto-engagement, you'll need to create a Reddit app.")
