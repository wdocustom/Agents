"""
Lead Generation Orchestrator - Coordinates all agents.
"""

import logging
from typing import List, Optional
from datetime import datetime
import csv
import os
from pathlib import Path

from models.lead import ConstructionLead
from agents.lead_discovery import LeadDiscoveryAgent
from agents.lead_qualifier import LeadQualifierAgent
from agents.data_enrichment import DataEnrichmentAgent
from config.settings import get_settings

logger = logging.getLogger(__name__)


class ConstructionLeadOrchestrator:
    """Orchestrates the lead generation process using multiple agents."""

    def __init__(
        self,
        target_location: Optional[str] = None,
        radius_miles: Optional[float] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            target_location: Target location (overrides settings)
            radius_miles: Search radius (overrides settings)
        """
        self.settings = get_settings()

        # Initialize agents
        self.discovery_agent = LeadDiscoveryAgent()
        self.qualifier_agent = LeadQualifierAgent()
        self.enrichment_agent = DataEnrichmentAgent()

        # Store results
        self.all_leads: List[ConstructionLead] = []
        self.qualified_leads: List[ConstructionLead] = []

        logger.info("Lead generation orchestrator initialized")

    def run(
        self,
        max_leads: int = 25,
        enrich_leads: bool = True,
        save_output: bool = True
    ) -> List[ConstructionLead]:
        """
        Run the complete lead generation pipeline.

        Args:
            max_leads: Maximum number of leads to discover
            enrich_leads: Whether to enrich leads with additional data
            save_output: Whether to save output to file

        Returns:
            List of qualified leads
        """
        logger.info("="*60)
        logger.info("STARTING CONSTRUCTION LEAD GENERATION")
        logger.info("="*60)
        logger.info(f"Target: {self.settings.get_target_location_str()}")
        logger.info(f"Radius: {self.settings.target_radius_miles} miles")
        logger.info(f"Max leads: {max_leads}")
        logger.info("="*60)

        start_time = datetime.now()

        try:
            # Step 1: Discover leads
            logger.info("\n[STEP 1/4] Discovering leads...")
            self.all_leads = self.discovery_agent.discover_leads(max_leads=max_leads)
            logger.info(f"✓ Discovered {len(self.all_leads)} leads")

            # Step 2: Qualify leads
            logger.info("\n[STEP 2/4] Qualifying and scoring leads...")
            self.qualified_leads = self.qualifier_agent.qualify_leads(self.all_leads)
            logger.info(
                f"✓ Qualified {len(self.qualified_leads)} leads "
                f"(min score: {self.settings.min_lead_score})"
            )

            # Step 3: Enrich leads (optional)
            if enrich_leads and self.qualified_leads:
                logger.info(
                    f"\n[STEP 3/4] Enriching {len(self.qualified_leads)} qualified leads..."
                )
                enriched_count = 0
                for lead in self.qualified_leads:
                    try:
                        self.enrichment_agent.enrich_lead(lead)
                        enriched_count += 1
                    except Exception as e:
                        logger.error(f"Error enriching {lead.company_name}: {e}")

                logger.info(f"✓ Enriched {enriched_count} leads")
            else:
                logger.info("\n[STEP 3/4] Skipping enrichment")

            # Step 4: Save results
            if save_output and self.qualified_leads:
                logger.info("\n[STEP 4/4] Saving results...")
                output_file = self._save_results()
                logger.info(f"✓ Results saved to: {output_file}")
            else:
                logger.info("\n[STEP 4/4] Skipping save")

            # Summary
            duration = (datetime.now() - start_time).total_seconds()
            self._print_summary(duration)

            return self.qualified_leads

        except Exception as e:
            logger.error(f"Lead generation failed: {e}", exc_info=True)
            raise

    def _save_results(self) -> str:
        """
        Save qualified leads to CSV file.

        Returns:
            Path to output file
        """
        # Create output directory
        output_dir = Path(self.settings.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"construction_leads_{timestamp}.csv"

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if not self.qualified_leads:
                return str(output_file)

            # Get field names from first lead
            fieldnames = list(self.qualified_leads[0].to_csv_row().keys())

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for lead in self.qualified_leads:
                writer.writerow(lead.to_csv_row())

        logger.info(f"Saved {len(self.qualified_leads)} leads to {output_file}")
        return str(output_file)

    def _print_summary(self, duration: float):
        """
        Print summary of lead generation results.

        Args:
            duration: Duration in seconds
        """
        logger.info("\n" + "="*60)
        logger.info("LEAD GENERATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total leads discovered: {len(self.all_leads)}")
        logger.info(f"Qualified leads: {len(self.qualified_leads)}")
        logger.info(
            f"Qualification rate: "
            f"{len(self.qualified_leads)/len(self.all_leads)*100:.1f}%"
            if self.all_leads else "0%"
        )
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info("="*60)

        if self.qualified_leads:
            logger.info("\nTOP QUALIFIED LEADS:")
            logger.info("-"*60)

            # Sort by score
            sorted_leads = sorted(
                self.qualified_leads,
                key=lambda x: x.score.total_score if x.score else 0,
                reverse=True
            )

            for i, lead in enumerate(sorted_leads[:5], 1):
                score = lead.score.total_score if lead.score else 0
                distance = lead.location.distance_from_target or 0

                logger.info(
                    f"{i}. {lead.company_name} "
                    f"(Score: {score}/100, Distance: {distance:.1f} mi)"
                )
                logger.info(f"   Project: {lead.project.description[:80]}...")
                if lead.project.estimated_budget:
                    logger.info(
                        f"   Budget: ${lead.project.estimated_budget:,.0f}"
                    )
                logger.info("")

        logger.info("="*60)

    def get_lead_statistics(self) -> dict:
        """
        Get statistics about discovered and qualified leads.

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_discovered': len(self.all_leads),
            'total_qualified': len(self.qualified_leads),
            'qualification_rate': (
                len(self.qualified_leads) / len(self.all_leads)
                if self.all_leads else 0
            ),
            'average_score': 0,
            'average_distance': 0,
            'total_estimated_value': 0,
        }

        if self.qualified_leads:
            scores = [
                lead.score.total_score
                for lead in self.qualified_leads
                if lead.score
            ]
            stats['average_score'] = sum(scores) / len(scores) if scores else 0

            distances = [
                lead.location.distance_from_target
                for lead in self.qualified_leads
                if lead.location.distance_from_target is not None
            ]
            stats['average_distance'] = sum(distances) / len(distances) if distances else 0

            budgets = [
                lead.project.estimated_budget
                for lead in self.qualified_leads
                if lead.project.estimated_budget
            ]
            stats['total_estimated_value'] = sum(budgets) if budgets else 0

        return stats

    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Export qualified leads to JSON format.

        Args:
            filename: Optional output filename

        Returns:
            Path to output file
        """
        import json

        if filename is None:
            output_dir = Path(self.settings.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"construction_leads_{timestamp}.json"

        leads_data = [lead.model_dump(mode='json') for lead in self.qualified_leads]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, indent=2, default=str)

        logger.info(f"Exported {len(self.qualified_leads)} leads to {filename}")
        return str(filename)
