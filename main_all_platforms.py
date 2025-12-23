#!/usr/bin/env python3
"""
Multi-platform lead finder - Reddit + Craigslist + Nextdoor instructions
"""

import sys
from agents.simple_reddit_scraper import SimpleRedditScraper
from agents.craigslist_scraper import CraigslistScraper
from agents.nextdoor_scraper import NextdoorScraper
from agents.keyword_detector import KeywordDetector
from agents.response_generator import ResponseGenerator
from agents.engagement_manager import EngagementManager
from config.settings import get_settings
from utils.logger import setup_logging


def main():
    """Main execution function."""
    settings = get_settings()
    setup_logging(log_level="INFO", log_file=settings.log_file, log_to_console=True)

    print("="*70)
    print("  MULTI-PLATFORM CONSTRUCTION LEAD FINDER")
    print("  Reddit + Craigslist + Nextdoor")
    print("="*70)
    print()

    try:
        # Initialize scrapers
        reddit_scraper = SimpleRedditScraper()
        craigslist_scraper = CraigslistScraper()
        nextdoor_scraper = NextdoorScraper()

        keyword_detector = KeywordDetector()
        response_generator = ResponseGenerator()
        engagement_manager = EngagementManager()

        all_opportunities = []

        # Scrape Reddit
        print("[1/3] Scraping Reddit...")
        reddit_opps = reddit_scraper.monitor_all(hours_back=48, limit_per_sub=50)
        all_opportunities.extend(reddit_opps)
        print(f"  ✓ Found {len(reddit_opps)} Reddit posts\n")

        # Scrape Craigslist
        print("[2/3] Scraping Craigslist...")
        craigslist_opps = craigslist_scraper.monitor_all()
        all_opportunities.extend(craigslist_opps)
        print(f"  ✓ Found {len(craigslist_opps)} Craigslist posts\n")

        # Nextdoor (manual)
        print("[3/3] Nextdoor (manual monitoring)")
        print("  ℹ Nextdoor requires manual monitoring")
        print("  See instructions at end of this report\n")

        if not all_opportunities:
            print("⚠ No posts found. Try again later.")
            return 1

        # Analyze
        print(f"[ANALYSIS] Analyzing {len(all_opportunities)} total posts...")
        analyzed = keyword_detector.batch_analyze(all_opportunities)
        relevant = keyword_detector.filter_relevant(analyzed, min_score=50, require_omaha=False)
        print(f"  ✓ Found {len(relevant)} relevant opportunities\n")

        if not relevant:
            print("⚠ No relevant opportunities found.")
            print("  Try again tomorrow - new posts appear daily!\n")

            # Still show Nextdoor instructions
            print("\n" + "="*70)
            print("NEXTDOOR MONITORING INSTRUCTIONS")
            print("="*70)
            nextdoor = NextdoorScraper()
            print(nextdoor.get_manual_instructions())
            return 1

        # Generate responses
        print("[RESPONSES] Generating responses...")
        response_generator.batch_generate(relevant)
        print("  ✓ Responses generated\n")

        # Save
        print("[EXPORT] Saving results...")
        output_file = engagement_manager.export_opportunities(relevant)
        print(f"  ✓ Saved to: {output_file}\n")

        # Summary
        print("="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"Reddit: {len(reddit_opps)} posts")
        print(f"Craigslist: {len(craigslist_opps)} posts")
        print(f"Total Analyzed: {len(all_opportunities)}")
        print(f"Relevant Opportunities: {len(relevant)}")
        print("="*70)

        # Show top opportunities
        print("\nTOP OPPORTUNITIES:")
        print("-"*70)

        for i, opp in enumerate(relevant[:10], 1):
            platform_name = opp.platform.upper()
            if opp.subreddit:
                location = f"r/{opp.subreddit}"
            elif opp.group_name:
                location = opp.group_name
            else:
                location = "Unknown"

            print(f"\n{i}. [{platform_name}] {opp.title}")
            print(f"   Score: {opp.relevance_score}/100")
            print(f"   Location: {location}")
            print(f"   URL: {opp.url}")
            if opp.keywords_matched:
                print(f"   Keywords: {', '.join(opp.keywords_matched[:3])}")

        print("\n" + "="*70)
        print(f"✓ Found {len(relevant)} opportunities!")
        print(f"  Check: {output_file}")
        print("="*70)

        # Nextdoor instructions
        print("\n" + "="*70)
        print("NEXTDOOR MONITORING INSTRUCTIONS")
        print("="*70)
        nextdoor = NextdoorScraper()
        print(nextdoor.get_manual_instructions())

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
