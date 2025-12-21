"""
Data Enrichment Agent - Enriches leads with additional information.
"""

import logging
from typing import Optional
from anthropic import Anthropic

from models.lead import ConstructionLead, ContactInfo
from tools.web_search import WebSearchTool
from config.settings import get_settings

logger = logging.getLogger(__name__)


class DataEnrichmentAgent:
    """Agent responsible for enriching lead data with additional information."""

    def __init__(self):
        """Initialize the Data Enrichment Agent."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)
        self.search_tool = WebSearchTool(self.settings.serper_api_key)

    def enrich_lead(self, lead: ConstructionLead) -> ConstructionLead:
        """
        Enrich a lead with additional information.

        Args:
            lead: Lead to enrich

        Returns:
            Enriched lead
        """
        logger.info(f"Enriching lead: {lead.company_name}")

        try:
            # 1. Find company contact information
            if not lead.contact_info or not lead.contact_info.email:
                contact_info = self._find_contact_info(lead)
                if contact_info:
                    lead.contact_info = contact_info

            # 2. Enrich project details
            lead = self._enrich_project_details(lead)

            # 3. Add tags for categorization
            lead.tags = self._generate_tags(lead)

            logger.info(f"Enrichment complete for: {lead.company_name}")

        except Exception as e:
            logger.error(f"Error enriching lead {lead.company_name}: {e}")

        return lead

    def _find_contact_info(self, lead: ConstructionLead) -> Optional[ContactInfo]:
        """
        Find contact information for a company.

        Args:
            lead: Lead to find contact info for

        Returns:
            ContactInfo or None
        """
        try:
            # Search for company contact info
            search_query = f"{lead.company_name} {lead.location.city} contact email phone"
            results = self.search_tool.search_google(search_query, num_results=3)

            if not results:
                return None

            # Use Claude to extract contact information
            search_context = "\n\n".join([
                f"Title: {r['title']}\nSnippet: {r['snippet']}"
                for r in results[:3]
            ])

            extraction_prompt = f"""
            Find contact information for {lead.company_name} from these search results:

            {search_context}

            Extract:
            - Contact name (if available)
            - Email address
            - Phone number
            - Job title/role

            Return ONLY the information found, or say "NO_INFO" if no contact details are found.
            """

            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=300,
                messages=[{"role": "user", "content": extraction_prompt}]
            )

            response_text = message.content[0].text

            if "NO_INFO" in response_text:
                return None

            # Parse response into ContactInfo
            contact = self._parse_contact_response(response_text, lead.company_name)
            return contact

        except Exception as e:
            logger.error(f"Error finding contact info: {e}")
            return None

    def _parse_contact_response(
        self,
        response: str,
        company_name: str
    ) -> ContactInfo:
        """
        Parse Claude's contact extraction response.

        Args:
            response: Claude's response
            company_name: Name of the company

        Returns:
            ContactInfo object
        """
        import re

        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response)
        email = email_match.group(0) if email_match else None

        # Extract phone
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', response)
        phone = phone_match.group(0) if phone_match else None

        # Try to extract name
        name_match = re.search(r"(?:Contact|Name)[:\s]+(.+?)(?:\n|Email|Phone|$)", response, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else None

        contact = ContactInfo(
            company=company_name,
            email=email,
            phone=phone,
            name=name
        )

        return contact

    def _enrich_project_details(self, lead: ConstructionLead) -> ConstructionLead:
        """
        Enrich project details with additional information.

        Args:
            lead: Lead to enrich

        Returns:
            Lead with enriched project details
        """
        try:
            # If we have a source URL, extract more details
            if lead.source_url:
                content = self.search_tool.extract_page_content(lead.source_url)

                if content:
                    enrichment_prompt = f"""
                    Analyze this content about a construction project and extract details:

                    {content[:3000]}

                    Extract:
                    - More detailed project description
                    - Budget/cost estimates
                    - Square footage or project size
                    - Timeline information
                    - Project start/completion dates

                    Provide concise, factual information only.
                    """

                    message = self.client.messages.create(
                        model=self.settings.claude_model,
                        max_tokens=500,
                        messages=[{"role": "user", "content": enrichment_prompt}]
                    )

                    enrichment_text = message.content[0].text

                    # Update project description if current one is brief
                    if len(lead.project.description) < 100 and enrichment_text:
                        lead.project.description = enrichment_text[:500]

        except Exception as e:
            logger.error(f"Error enriching project details: {e}")

        return lead

    def _generate_tags(self, lead: ConstructionLead) -> list[str]:
        """
        Generate relevant tags for a lead.

        Args:
            lead: Lead to tag

        Returns:
            List of tags
        """
        tags = []

        # Project type tags
        tags.append(lead.project.project_type)

        # Size tags
        if lead.project.estimated_budget:
            if lead.project.estimated_budget >= 10_000_000:
                tags.append("large-budget")
            elif lead.project.estimated_budget >= 5_000_000:
                tags.append("medium-budget")
            else:
                tags.append("small-budget")

        # Location tags
        if lead.location.distance_from_target:
            if lead.location.distance_from_target <= 10:
                tags.append("local")
            elif lead.location.distance_from_target <= 25:
                tags.append("metro-area")
            else:
                tags.append("outer-radius")

        # Timeline tags
        if lead.project.timeline_urgency:
            urgency = lead.project.timeline_urgency.lower()
            if urgency in ['immediate', 'urgent', 'asap']:
                tags.append("urgent")
            elif urgency in ['soon', 'planned']:
                tags.append("upcoming")

        # Score-based tags
        if lead.score:
            if lead.score.total_score >= 80:
                tags.append("high-priority")
            elif lead.score.total_score >= 70:
                tags.append("priority")

        return tags
