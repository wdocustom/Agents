#!/usr/bin/env python3
"""
Simple social media monitoring - NO REDDIT CREDENTIALS NEEDED!
Uses web scraping instead of Reddit API.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from agents.simple_reddit_scraper import SimpleRedditScraper
from agents.keyword_detector import KeywordDetector
from agents.response_generator import ResponseGenerator
from agents.engagement_manager import EngagementManager
from config.settings import get_settings
from utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Simple social media monitoring (no Reddit credentials needed!)'
    )

    parser.add_argument(
        '--hours-back',
        type=int,
        default=48,
        help='Hours back to search (default: 48)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=60,
        help='Minimum relevance score (0-100, default: 60)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # Load settings
    settings = get_settings()
    settings.min_lead_score = args.min_score

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=settings.log_file,
        log_to_console=True
    )

    print("="*70)
    print("  SIMPLE REDDIT MONITORING (NO CREDENTIALS NEEDED!)")
    print("  Construction Services - Omaha, Nebraska")
    print("="*70)
    print(f"\nUsing web scraping (no Reddit app required)")
    print(f"Hours back: {args.hours_back}")
    print(f"Min Score: {settings.min_lead_score}/100")
    print("="*70)
    print()

    try:
        # Initialize components
        scraper = SimpleRedditScraper()
        keyword_detector = KeywordDetector()
        response_generator = ResponseGenerator()
        engagement_manager = EngagementManager()

        # Step 1: Scrape Reddit
        print("\n[STEP 1/4] Scraping Reddit for posts...")
        opportunities = scraper.monitor_all(
            hours_back=args.hours_back,
            limit_per_sub=50
        )
        print(f"✓ Found {len(opportunities)} total posts")

        if not opportunities:
            print("\n⚠ No posts found. Try:")
            print("  - Increasing hours back: --hours-back 72")
            print("  - Trying again later")
            return 1

        # Step 2: Analyze and filter
        print("\n[STEP 2/4] Analyzing posts with AI...")
        analyzed = keyword_detector.batch_analyze(opportunities)
        relevant = keyword_detector.filter_relevant(
            analyzed,
            min_score=settings.min_lead_score,
            require_omaha=True
        )
        print(f"✓ Found {len(relevant)} relevant opportunities")

        if not relevant:
            print("\n⚠ No relevant opportunities found. Try:")
            print("  - Lowering score: --min-score 50")
            print("  - Checking more hours: --hours-back 72")
            return 1

        # Step 3: Generate responses
        print("\n[STEP 3/4] Generating responses...")
        response_generator.batch_generate(relevant)
        print("✓ Responses generated")

        # Step 4: Export
        print("\n[STEP 4/4] Exporting results...")
        output_file = engagement_manager.export_opportunities(relevant)
        print(f"✓ Saved to: {output_file}")

        # Summary
        print("\n" + "="*70)
        print("  RESULTS")
        print("="*70)
        print(f"Total Posts: {len(opportunities)}")
        print(f"Relevant Opportunities: {len(relevant)}")
        print(f"Relevance Rate: {len(relevant)/len(opportunities)*100:.1f}%")
        print("="*70)

        # Show top opportunities
        print("\nTOP OPPORTUNITIES:")
        print("-" * 70)

        for i, opp in enumerate(relevant[:5], 1):
            print(f"\n{i}. [{opp.subreddit}] {opp.title}")
            print(f"   Score: {opp.relevance_score}/100")
            print(f"   Posted: {opp.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   URL: {opp.url}")
            if opp.keywords_matched:
                print(f"   Keywords: {', '.join(opp.keywords_matched[:3])}")

        print()
        print("="*70)
        print(f"\n✓ Found {len(relevant)} opportunities!")
        print(f"  Check: {output_file}")
        print("\n  To engage:")
        print("    1. Open the CSV file")
        print("    2. Review high-scoring opportunities")
        print("    3. Click the URLs")
        print("    4. Post the suggested responses (customize them!)")
        print("="*70)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        return 130

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
