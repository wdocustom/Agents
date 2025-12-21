#!/usr/bin/env python3
"""
Main entry point for the Social Media Lead Monitoring system.

This script monitors social media platforms (Reddit, Facebook) for construction
service requests in Omaha, Nebraska.
"""

import argparse
import sys
from pathlib import Path

from agents.social_media_orchestrator import SocialMediaOrchestrator
from config.settings import get_settings
from utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Social media lead monitoring for construction services in Omaha, NE',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor Reddit only (recommended to start)
  python main.py --mode monitor --platforms reddit

  # Monitor continuously every 15 minutes
  python main.py --mode monitor --continuous --interval 15

  # Monitor with auto-engagement (WARNING: read docs first!)
  python main.py --mode engage --platforms reddit

  # Monitor specific platforms
  python main.py --mode monitor --platforms reddit,facebook
        """
    )

    parser.add_argument(
        '--mode',
        choices=['monitor', 'engage'],
        default='monitor',
        help='Mode: monitor only (safe) or engage (auto-comment, risky)'
    )

    parser.add_argument(
        '--platforms',
        type=str,
        default='reddit',
        help='Platforms to monitor (comma-separated): reddit,facebook'
    )

    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously with periodic checks'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Minutes between checks in continuous mode (default: 15)'
    )

    parser.add_argument(
        '--hours-back',
        type=int,
        default=24,
        help='Hours back to search (default: 24)'
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

    # Override settings from args
    if args.min_score:
        settings.min_lead_score = args.min_score

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=settings.log_file,
        log_to_console=True
    )

    # Parse platforms
    platforms = [p.strip().lower() for p in args.platforms.split(',')]

    # Determine auto-engage
    auto_engage = (args.mode == 'engage')

    # Warnings
    print("="*70)
    print("  SOCIAL MEDIA LEAD MONITORING SYSTEM")
    print("  Construction Services - Omaha, Nebraska")
    print("="*70)
    print(f"\nMode: {args.mode.upper()}")
    print(f"Platforms: {', '.join(platforms)}")
    print(f"Min Relevance Score: {settings.min_lead_score}/100")

    if auto_engage:
        print("\n" + "!"*70)
        print("  WARNING: AUTO-ENGAGEMENT ENABLED")
        print("!"*70)
        print("Auto-engagement may violate platform Terms of Service.")
        print("You could be banned or suspended.")
        print("Use at your own risk. Press Ctrl+C to cancel, or wait 5 seconds...")
        print("!"*70)

        import time
        try:
            for i in range(5, 0, -1):
                print(f"\rStarting in {i}...  ", end='', flush=True)
                time.sleep(1)
            print("\rStarting now!       ")
        except KeyboardInterrupt:
            print("\n\nCancelled by user. Exiting.")
            return 0

    print("="*70)
    print()

    try:
        # Initialize orchestrator
        orchestrator = SocialMediaOrchestrator()

        if args.continuous:
            # Run continuously
            orchestrator.run_continuous(
                platforms=platforms,
                interval_minutes=args.interval,
                auto_engage=auto_engage
            )
        else:
            # Single run
            opportunities = orchestrator.monitor(
                platforms=platforms,
                hours_back=args.hours_back,
                auto_engage=auto_engage
            )

            # Print results
            stats = orchestrator.get_statistics()

            print("\n" + "="*70)
            print("  FINAL RESULTS")
            print("="*70)
            print(f"Total Opportunities Found: {stats['total_opportunities']}")
            print(f"Relevant Opportunities: {stats['relevant_opportunities']}")
            print(f"Relevance Rate: {stats['relevance_rate']*100:.1f}%")
            print(f"Average Relevance Score: {stats['average_relevance_score']:.1f}/100")
            print(f"High-Priority Opportunities: {stats['high_priority_count']}")

            if auto_engage:
                print(f"\nEngagements Today: {stats['today_engagements']}")
                print(f"Remaining Today: {stats['remaining_today']}")

            print("="*70)

            if opportunities:
                print(f"\n✓ Found {len(opportunities)} relevant opportunities!")
                print(f"  Check the output directory for detailed results.")
                print(f"\n  Review opportunities in: output/opportunities_[timestamp].csv")
                print(f"\n  To engage manually:")
                print(f"    1. Review the CSV file")
                print(f"    2. Open the URLs for high-scoring opportunities")
                print(f"    3. Post the suggested responses (customize as needed)")
                return 0
            else:
                print("\n⚠ No relevant opportunities found. Try:")
                print("  - Checking different hours back (--hours-back 48)")
                print("  - Lowering minimum score (--min-score 50)")
                print("  - Running again later")
                return 1

    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled by user")
        return 130

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
