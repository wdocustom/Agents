#!/usr/bin/env python3
"""
Main entry point for the Construction Lead Generation system.

This script runs the AI agents to discover, qualify, and manage
construction leads in the Omaha, Nebraska area.
"""

import argparse
import sys
from pathlib import Path

from agents.orchestrator import ConstructionLeadOrchestrator
from config.settings import get_settings
from utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AI-powered construction lead generation for Omaha, NE'
    )

    parser.add_argument(
        '--max-leads',
        type=int,
        default=25,
        help='Maximum number of leads to discover (default: 25)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=60,
        help='Minimum qualification score (0-100, default: 60)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: auto-generated in ./output/)'
    )

    parser.add_argument(
        '--no-enrich',
        action='store_true',
        help='Skip lead enrichment step'
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'both'],
        default='csv',
        help='Output format (default: csv)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--radius',
        type=float,
        default=35.0,
        help='Search radius in miles (default: 35)'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # Load settings
    settings = get_settings()

    # Override settings from args
    if args.radius:
        settings.target_radius_miles = args.radius
    if args.min_score:
        settings.min_lead_score = args.min_score

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=settings.log_file,
        log_to_console=True
    )

    print("="*70)
    print("  CONSTRUCTION LEAD GENERATION SYSTEM")
    print("  AI-Powered Lead Discovery for Omaha, Nebraska")
    print("="*70)
    print(f"\nTarget Location: {settings.get_target_location_str()}")
    print(f"Search Radius: {settings.target_radius_miles} miles")
    print(f"Max Leads: {args.max_leads}")
    print(f"Min Qualification Score: {settings.min_lead_score}/100")
    print(f"Enrichment: {'Disabled' if args.no_enrich else 'Enabled'}")
    print(f"Output Format: {args.format.upper()}")
    print("="*70)
    print()

    try:
        # Initialize orchestrator
        orchestrator = ConstructionLeadOrchestrator()

        # Run lead generation
        qualified_leads = orchestrator.run(
            max_leads=args.max_leads,
            enrich_leads=not args.no_enrich,
            save_output=True
        )

        # Export in requested format
        if args.format in ['json', 'both'] and qualified_leads:
            json_file = orchestrator.export_to_json(args.output)
            print(f"\n✓ JSON export saved: {json_file}")

        # Get statistics
        stats = orchestrator.get_lead_statistics()

        # Print final summary
        print("\n" + "="*70)
        print("  FINAL RESULTS")
        print("="*70)
        print(f"Total Leads Discovered: {stats['total_discovered']}")
        print(f"Qualified Leads: {stats['total_qualified']}")
        print(f"Qualification Rate: {stats['qualification_rate']*100:.1f}%")
        print(f"Average Lead Score: {stats['average_score']:.1f}/100")
        print(f"Average Distance: {stats['average_distance']:.1f} miles")
        if stats['total_estimated_value']:
            print(
                f"Total Estimated Project Value: "
                f"${stats['total_estimated_value']:,.0f}"
            )
        print("="*70)

        if qualified_leads:
            print(f"\n✓ Successfully generated {len(qualified_leads)} qualified leads!")
            print(f"  Check the output directory for your results.")
            return 0
        else:
            print("\n⚠ No qualified leads found. Try:")
            print("  - Increasing search radius (--radius)")
            print("  - Lowering minimum score (--min-score)")
            print("  - Increasing max leads (--max-leads)")
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
