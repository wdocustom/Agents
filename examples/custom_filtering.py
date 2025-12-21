#!/usr/bin/env python3
"""
Example of custom lead filtering and analysis.
"""

from agents.orchestrator import ConstructionLeadOrchestrator
from utils.logger import setup_logging


def main():
    """Run lead generation with custom filtering."""

    setup_logging(log_level="INFO")

    # Initialize orchestrator
    orchestrator = ConstructionLeadOrchestrator()

    # Generate leads
    print("Generating leads...")
    qualified_leads = orchestrator.run(max_leads=20)

    # Filter for high-value projects
    high_value_leads = [
        lead for lead in qualified_leads
        if lead.project.estimated_budget
        and lead.project.estimated_budget >= 5_000_000
    ]

    print(f"\nHigh-Value Projects (>$5M):")
    print("="*60)
    for lead in high_value_leads:
        print(f"\n{lead.company_name}")
        print(f"Budget: ${lead.project.estimated_budget:,.0f}")
        print(f"Project: {lead.project.description[:100]}...")
        print(f"Score: {lead.score.total_score}/100")

    # Filter for urgent projects
    urgent_leads = [
        lead for lead in qualified_leads
        if lead.project.timeline_urgency
        and lead.project.timeline_urgency.lower() in ['immediate', 'urgent', 'asap']
    ]

    print(f"\n\nUrgent Projects:")
    print("="*60)
    for lead in urgent_leads:
        print(f"\n{lead.company_name}")
        print(f"Timeline: {lead.project.timeline_urgency}")
        print(f"Project: {lead.project.description[:100]}...")

    # Filter for local projects (within 15 miles)
    local_leads = [
        lead for lead in qualified_leads
        if lead.location.distance_from_target
        and lead.location.distance_from_target <= 15
    ]

    print(f"\n\nLocal Projects (<15 miles):")
    print("="*60)
    for lead in local_leads:
        print(f"\n{lead.company_name}")
        print(f"Distance: {lead.location.distance_from_target:.1f} miles")
        print(f"Location: {lead.location.address}")

    # Statistics
    print(f"\n\nFiltering Summary:")
    print("="*60)
    print(f"Total Qualified: {len(qualified_leads)}")
    print(f"High-Value (>$5M): {len(high_value_leads)}")
    print(f"Urgent Timeline: {len(urgent_leads)}")
    print(f"Local (<15mi): {len(local_leads)}")


if __name__ == '__main__':
    main()
