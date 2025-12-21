"""
Lead Qualifier Agent - Scores and qualifies construction leads.
"""

import logging
from typing import List
from anthropic import Anthropic

from models.lead import ConstructionLead, LeadScore, LeadStatus
from config.settings import get_settings

logger = logging.getLogger(__name__)


class LeadQualifierAgent:
    """Agent responsible for qualifying and scoring construction leads."""

    def __init__(self):
        """Initialize the Lead Qualifier Agent."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)

    def qualify_leads(self, leads: List[ConstructionLead]) -> List[ConstructionLead]:
        """
        Qualify and score a list of leads.

        Args:
            leads: List of leads to qualify

        Returns:
            List of qualified leads with scores
        """
        logger.info(f"Qualifying {len(leads)} leads")

        qualified_leads = []
        for lead in leads:
            try:
                scored_lead = self._score_lead(lead)
                if scored_lead.is_qualified(self.settings.min_lead_score):
                    scored_lead.status = LeadStatus.QUALIFIED
                    qualified_leads.append(scored_lead)
                    logger.info(
                        f"Qualified: {scored_lead.company_name} "
                        f"(Score: {scored_lead.score.total_score})"
                    )
                else:
                    scored_lead.status = LeadStatus.DISQUALIFIED
                    logger.debug(
                        f"Disqualified: {scored_lead.company_name} "
                        f"(Score: {scored_lead.score.total_score})"
                    )
            except Exception as e:
                logger.error(f"Error qualifying lead {lead.company_name}: {e}")

        logger.info(f"Qualified {len(qualified_leads)} out of {len(leads)} leads")
        return qualified_leads

    def _score_lead(self, lead: ConstructionLead) -> ConstructionLead:
        """
        Score a single lead based on criteria.

        Args:
            lead: Lead to score

        Returns:
            Lead with updated score
        """
        score_breakdown = LeadScore()

        # 1. Project Size Score (0-30 points)
        score_breakdown.project_size_score = self._score_project_size(lead)

        # 2. Timeline Score (0-20 points)
        score_breakdown.timeline_score = self._score_timeline(lead)

        # 3. Location Score (0-20 points)
        score_breakdown.location_score = self._score_location(lead)

        # 4. Contact Quality Score (0-15 points)
        score_breakdown.contact_quality_score = self._score_contact_quality(lead)

        # 5. Company Fit Score (0-15 points)
        score_breakdown.company_fit_score = self._score_company_fit(lead)

        # Calculate total
        score_breakdown.total_score = (
            score_breakdown.project_size_score +
            score_breakdown.timeline_score +
            score_breakdown.location_score +
            score_breakdown.contact_quality_score +
            score_breakdown.company_fit_score
        )

        # Add notes
        score_breakdown.notes = self._generate_score_notes(lead, score_breakdown)

        lead.score = score_breakdown
        return lead

    def _score_project_size(self, lead: ConstructionLead) -> int:
        """
        Score based on project size (0-30 points).

        Args:
            lead: Lead to score

        Returns:
            Score for project size
        """
        project = lead.project

        # Score based on estimated budget
        if project.estimated_budget:
            if project.estimated_budget >= 20_000_000:
                return 30
            elif project.estimated_budget >= 10_000_000:
                return 25
            elif project.estimated_budget >= 5_000_000:
                return 20
            elif project.estimated_budget >= 1_000_000:
                return 15
            elif project.estimated_budget >= 500_000:
                return 10
            else:
                return 5

        # Score based on square footage if no budget
        if project.square_footage:
            if project.square_footage >= 100_000:
                return 25
            elif project.square_footage >= 50_000:
                return 20
            elif project.square_footage >= 25_000:
                return 15
            elif project.square_footage >= 10_000:
                return 10
            else:
                return 5

        # Default score if no size information
        return 10

    def _score_timeline(self, lead: ConstructionLead) -> int:
        """
        Score based on project timeline (0-20 points).

        Args:
            lead: Lead to score

        Returns:
            Score for timeline urgency
        """
        urgency = lead.project.timeline_urgency

        if urgency:
            urgency_lower = urgency.lower()
            if urgency_lower in ['immediate', 'urgent', 'asap']:
                return 20
            elif urgency_lower in ['soon', 'short-term', 'planned']:
                return 15
            elif urgency_lower in ['medium-term', 'future']:
                return 10
            else:
                return 5

        # Default if no timeline info
        return 10

    def _score_location(self, lead: ConstructionLead) -> int:
        """
        Score based on location proximity (0-20 points).

        Args:
            lead: Lead to score

        Returns:
            Score for location
        """
        distance = lead.location.distance_from_target

        if distance is None:
            return 10  # Default score

        if distance <= 10:
            return 20
        elif distance <= 20:
            return 15
        elif distance <= 30:
            return 10
        elif distance <= 35:
            return 5
        else:
            return 0

    def _score_contact_quality(self, lead: ConstructionLead) -> int:
        """
        Score based on contact information quality (0-15 points).

        Args:
            lead: Lead to score

        Returns:
            Score for contact quality
        """
        if not lead.contact_info:
            return 5  # Base score even without contact info

        score = 5
        contact = lead.contact_info

        if contact.name:
            score += 3
        if contact.email:
            score += 4
        if contact.phone:
            score += 3

        return min(score, 15)

    def _score_company_fit(self, lead: ConstructionLead) -> int:
        """
        Score based on how well the project fits (0-15 points).

        Args:
            lead: Lead to score

        Returns:
            Score for company fit
        """
        project_type = lead.project.project_type

        # Preferred project types get higher scores
        preferred_types = ['commercial', 'industrial', 'mixed_use']
        moderate_types = ['renovation', 'new_build']

        if project_type in preferred_types:
            return 15
        elif project_type in moderate_types:
            return 10
        else:
            return 8

    def _generate_score_notes(
        self,
        lead: ConstructionLead,
        score: LeadScore
    ) -> List[str]:
        """
        Generate notes explaining the score.

        Args:
            lead: The lead being scored
            score: The score breakdown

        Returns:
            List of note strings
        """
        notes = []

        # Project size notes
        if score.project_size_score >= 25:
            notes.append("Large project - high value opportunity")
        elif score.project_size_score <= 10:
            notes.append("Smaller project - may require less overhead")

        # Location notes
        if score.location_score >= 15:
            notes.append("Close proximity - lower travel costs")
        elif score.location_score <= 5:
            notes.append("Further distance - consider travel logistics")

        # Timeline notes
        if score.timeline_score >= 15:
            notes.append("Urgent timeline - quick action needed")

        # Contact notes
        if score.contact_quality_score <= 7:
            notes.append("Limited contact info - research needed")
        else:
            notes.append("Good contact information available")

        # Overall notes
        if score.total_score >= 80:
            notes.append("HIGH PRIORITY - Excellent fit")
        elif score.total_score >= 70:
            notes.append("Strong candidate - prioritize outreach")
        elif score.total_score >= 60:
            notes.append("Qualified lead - worth pursuing")

        return notes

    def analyze_lead_with_ai(self, lead: ConstructionLead) -> str:
        """
        Use Claude to provide additional analysis of a lead.

        Args:
            lead: Lead to analyze

        Returns:
            Analysis text from Claude
        """
        analysis_prompt = f"""
        Analyze this construction lead and provide recommendations:

        Company: {lead.company_name}
        Project Type: {lead.project.project_type}
        Description: {lead.project.description}
        Location: {lead.location.city}, {lead.location.state}
        Distance: {lead.location.distance_from_target} miles
        Budget: ${lead.project.estimated_budget:,.0f if lead.project.estimated_budget else 'Unknown'}
        Size: {lead.project.square_footage:,} sq ft if lead.project.square_footage else 'Unknown'
        Score: {lead.score.total_score if lead.score else 'Not scored'}/100

        Provide:
        1. Brief assessment of this opportunity
        2. Key strengths or concerns
        3. Recommended next steps
        """

        try:
            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return "Analysis unavailable"
