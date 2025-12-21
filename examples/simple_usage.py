#!/usr/bin/env python3
"""
Simple usage example for the Construction Lead Generation system.
"""

from agents.orchestrator import ConstructionLeadOrchestrator
from config.settings import get_settings
from utils.logger import setup_logging


def main():
    """Run a simple lead generation example."""

    # Setup logging
    setup_logging(log_level="INFO")

    # Initialize the orchestrator
    orchestrator = ConstructionLeadOrchestrator()

    # Run lead generation with default settings
    print("Generating construction leads for Omaha, NE...")
    qualified_leads = orchestrator.run(max_leads=10)

    # Display results
    print(f"\nFound {len(qualified_leads)} qualified leads:\n")

    for i, lead in enumerate(qualified_leads, 1):
        print(f"{i}. {lead.company_name}")
        print(f"   Score: {lead.score.total_score}/100")
        print(f"   Project: {lead.project.project_type}")
        print(f"   Location: {lead.location.city}, {lead.location.state}")
        print(f"   Distance: {lead.location.distance_from_target:.1f} miles")
        if lead.project.estimated_budget:
            print(f"   Budget: ${lead.project.estimated_budget:,.0f}")
        print()


if __name__ == '__main__':
    main()
