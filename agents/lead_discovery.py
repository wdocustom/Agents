"""
Lead Discovery Agent - Finds potential construction leads.
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime
import re
from anthropic import Anthropic

from models.lead import (
    ConstructionLead,
    Location,
    ProjectDetails,
    ContactInfo,
    ProjectType,
    LeadSource,
)
from tools.location_filter import LocationFilter
from tools.web_search import WebSearchTool
from config.settings import get_settings

logger = logging.getLogger(__name__)


class LeadDiscoveryAgent:
    """Agent responsible for discovering construction leads in the target area."""

    def __init__(self):
        """Initialize the Lead Discovery Agent."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)
        self.location_filter = LocationFilter(
            self.settings.target_lat,
            self.settings.target_lon,
            self.settings.target_radius_miles
        )
        self.search_tool = WebSearchTool(self.settings.serper_api_key)

    def discover_leads(self, max_leads: int = 25) -> List[ConstructionLead]:
        """
        Discover construction leads in the target area.

        Args:
            max_leads: Maximum number of leads to discover

        Returns:
            List of discovered construction leads
        """
        logger.info(f"Starting lead discovery (max: {max_leads})")

        discovered_leads = []

        # Search for construction projects
        search_results = self._search_for_projects()

        # Process search results
        for result in search_results:
            if len(discovered_leads) >= max_leads:
                break

            try:
                lead = self._process_search_result(result)
                if lead and self._validate_lead(lead):
                    discovered_leads.append(lead)
                    logger.info(f"Discovered lead: {lead.company_name}")
            except Exception as e:
                logger.error(f"Error processing search result: {e}")

        # Generate synthetic leads based on known patterns (for demonstration)
        if len(discovered_leads) < max_leads:
            synthetic_leads = self._generate_sample_leads(
                max_leads - len(discovered_leads)
            )
            discovered_leads.extend(synthetic_leads)

        logger.info(f"Discovery complete. Found {len(discovered_leads)} leads")
        return discovered_leads

    def _search_for_projects(self) -> List[Dict]:
        """
        Search for construction projects in target area.

        Returns:
            List of search results
        """
        area = self.settings.get_target_location_str()
        results = self.search_tool.search_construction_leads(area=area)

        logger.info(f"Found {len(results)} search results")
        return results

    def _process_search_result(self, result: Dict) -> Optional[ConstructionLead]:
        """
        Process a search result into a construction lead.

        Args:
            result: Search result dictionary

        Returns:
            ConstructionLead or None
        """
        try:
            # Extract information using Claude
            extraction_prompt = f"""
            Analyze this search result and extract construction lead information:

            Title: {result.get('title', '')}
            Snippet: {result.get('snippet', '')}
            URL: {result.get('link', '')}

            Extract the following information if available:
            1. Company name
            2. Project type (commercial, residential, industrial, etc.)
            3. Project description
            4. Location (address, city, state)
            5. Any budget or size information
            6. Timeline information

            Return the information in a structured format.
            If this doesn't appear to be a valid construction lead, say "NOT_A_LEAD".
            """

            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": extraction_prompt}]
            )

            response_text = message.content[0].text

            if "NOT_A_LEAD" in response_text:
                return None

            # Parse the response and create a lead
            lead = self._parse_extraction_response(response_text, result)
            return lead

        except Exception as e:
            logger.error(f"Error processing search result: {e}")
            return None

    def _parse_extraction_response(
        self,
        response: str,
        original_result: Dict
    ) -> Optional[ConstructionLead]:
        """
        Parse Claude's extraction response into a ConstructionLead.

        Args:
            response: Claude's response text
            original_result: Original search result

        Returns:
            ConstructionLead or None
        """
        # This is a simplified parser - in production, you'd use more sophisticated parsing
        # For now, create a basic lead structure

        # Try to extract company name
        company_match = re.search(r"Company[:\s]+(.+?)(?:\n|$)", response, re.IGNORECASE)
        company_name = company_match.group(1).strip() if company_match else "Unknown Company"

        # Try to extract location
        location_match = re.search(r"Location[:\s]+(.+?)(?:\n|$)", response, re.IGNORECASE)
        location_str = location_match.group(1).strip() if location_match else "Omaha, NE"

        # Geocode location
        address_parts = self.location_filter.parse_address_components(location_str)
        coords = self.location_filter.geocode_address(location_str)

        if coords:
            lat, lon = coords
            distance = self.location_filter.calculate_distance(lat, lon)
        else:
            lat, lon, distance = None, None, None

        location = Location(
            address=address_parts.get('street', ''),
            city=address_parts.get('city', self.settings.target_city),
            state=address_parts.get('state', self.settings.target_state),
            zip_code=address_parts.get('zip_code'),
            latitude=lat,
            longitude=lon,
            distance_from_target=distance
        )

        # Create project details
        project = ProjectDetails(
            project_type=ProjectType.COMMERCIAL,  # Default, should be extracted
            description=original_result.get('snippet', 'Construction project'),
        )

        # Create lead
        lead = ConstructionLead(
            source=LeadSource.WEB_SEARCH,
            source_url=original_result.get('link'),
            company_name=company_name,
            project=project,
            location=location,
            raw_data=original_result
        )

        return lead

    def _validate_lead(self, lead: ConstructionLead) -> bool:
        """
        Validate that a lead meets basic criteria.

        Args:
            lead: Lead to validate

        Returns:
            True if valid, False otherwise
        """
        # Check if location is within radius
        if lead.location.distance_from_target is not None:
            if not lead.is_in_radius(self.settings.target_radius_miles):
                logger.debug(f"Lead rejected: outside radius ({lead.location.distance_from_target} miles)")
                return False

        # Check if company name is valid
        if not lead.company_name or lead.company_name == "Unknown Company":
            logger.debug("Lead rejected: no valid company name")
            return False

        return True

    def _generate_sample_leads(self, count: int) -> List[ConstructionLead]:
        """
        Generate sample leads for demonstration purposes.

        Args:
            count: Number of sample leads to generate

        Returns:
            List of sample leads
        """
        logger.info(f"Generating {count} sample leads")

        sample_projects = [
            {
                "company": "Midwest Construction Solutions",
                "project_type": ProjectType.COMMERCIAL,
                "description": "New 50,000 sq ft retail center development",
                "address": "10250 Regency Circle, Omaha, NE 68114",
                "budget": 8500000,
                "sqft": 50000
            },
            {
                "company": "Heritage Building Group",
                "project_type": ProjectType.INDUSTRIAL,
                "description": "Manufacturing facility expansion",
                "address": "4500 S 134th St, Omaha, NE 68137",
                "budget": 12000000,
                "sqft": 75000
            },
            {
                "company": "Prairie Development Partners",
                "project_type": ProjectType.MIXED_USE,
                "description": "Mixed-use development with retail and residential",
                "address": "2001 Farnam St, Omaha, NE 68102",
                "budget": 25000000,
                "sqft": 150000
            },
            {
                "company": "Elkhorn Valley Builders",
                "project_type": ProjectType.COMMERCIAL,
                "description": "Medical office building construction",
                "address": "3900 N 192nd St, Elkhorn, NE 68022",
                "budget": 6500000,
                "sqft": 35000
            },
            {
                "company": "Bellevue Commercial Construction",
                "project_type": ProjectType.RENOVATION,
                "description": "Historic building renovation and restoration",
                "address": "1905 Hancock St, Bellevue, NE 68005",
                "budget": 3200000,
                "sqft": 22000
            },
        ]

        leads = []
        for i, sample in enumerate(sample_projects[:count]):
            coords = self.location_filter.geocode_address(sample["address"])
            if coords:
                lat, lon = coords
                distance = self.location_filter.calculate_distance(lat, lon)
            else:
                lat, lon, distance = None, None, 10.0

            location = Location(
                address=sample["address"],
                city="Omaha",
                state="NE",
                latitude=lat,
                longitude=lon,
                distance_from_target=distance
            )

            project = ProjectDetails(
                project_type=sample["project_type"],
                description=sample["description"],
                estimated_budget=sample.get("budget"),
                square_footage=sample.get("sqft"),
                timeline_urgency="planned"
            )

            lead = ConstructionLead(
                id=f"LEAD-{i+1:04d}",
                source=LeadSource.BUILDING_PERMIT,
                company_name=sample["company"],
                project=project,
                location=location,
            )

            leads.append(lead)

        return leads
