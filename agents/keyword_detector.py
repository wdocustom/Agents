"""
Keyword Detection Agent - Uses AI to identify relevant social media posts.
"""

import logging
import re
from typing import List, Set
from anthropic import Anthropic

from models.opportunity import SocialOpportunity
from config.settings import get_settings

logger = logging.getLogger(__name__)


class KeywordDetector:
    """Agent that detects and scores relevant keywords in social media posts."""

    def __init__(self):
        """Initialize the Keyword Detector."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)

    def get_construction_keywords(self) -> Set[str]:
        """
        Get comprehensive list of construction-related keywords.

        Returns:
            Set of keywords
        """
        keywords = {
            # Direct service requests
            "looking for contractor",
            "need contractor",
            "contractor recommendation",
            "contractor needed",
            "searching for contractor",

            # Tile work
            "tile work",
            "tile installer",
            "tile installation",
            "tile contractor",
            "tiling",
            "tile repair",
            "tile replacement",
            "retile",

            # Bathroom
            "bathroom remodel",
            "bathroom renovation",
            "bathroom contractor",
            "shower tile",
            "bathroom floor",
            "bathtub tile",

            # Kitchen
            "kitchen remodel",
            "kitchen renovation",
            "kitchen backsplash",
            "kitchen floor",

            # Flooring
            "flooring",
            "floor installation",
            "new flooring",
            "replace flooring",
            "laminate",
            "hardwood",
            "vinyl flooring",

            # General construction
            "home remodel",
            "home renovation",
            "renovation contractor",
            "remodeling",
            "handyman",
            "home improvement",
            "construction work",

            # Specific needs
            "need help with",
            "anyone know",
            "recommendations for",
            "looking to hire",
            "quote for",
            "estimate for",
        }

        return keywords

    def get_location_keywords(self) -> Set[str]:
        """
        Get Omaha-area location keywords.

        Returns:
            Set of location keywords
        """
        locations = {
            "omaha",
            "bellevue",
            "papillion",
            "la vista",
            "council bluffs",
            "elkhorn",
            "gretna",
            "ralston",
            "boys town",
            "west omaha",
            "east omaha",
            "north omaha",
            "south omaha",
            "midtown omaha",
            "downtown omaha",
            "nebraska",
            "68144", "68022", "68046", "68138", "68127",  # Zip codes
        }

        return locations

    def analyze_opportunity(
        self,
        opportunity: SocialOpportunity
    ) -> SocialOpportunity:
        """
        Analyze an opportunity and add keyword/location information.

        Args:
            opportunity: SocialOpportunity to analyze

        Returns:
            Updated opportunity with analysis
        """
        text_lower = opportunity.full_text.lower()

        # Check for construction keywords
        construction_keywords = self.get_construction_keywords()
        matched_keywords = [
            kw for kw in construction_keywords
            if kw.lower() in text_lower
        ]
        opportunity.keywords_matched = matched_keywords

        # Check for location keywords
        location_keywords = self.get_location_keywords()
        matched_locations = [
            loc for loc in location_keywords
            if loc.lower() in text_lower
        ]
        opportunity.location_mentions = matched_locations
        opportunity.is_omaha_related = len(matched_locations) > 0

        # Calculate relevance score using AI
        if matched_keywords:
            opportunity.relevance_score = self._calculate_relevance_score(opportunity)
        else:
            opportunity.relevance_score = 0

        return opportunity

    def _calculate_relevance_score(
        self,
        opportunity: SocialOpportunity
    ) -> int:
        """
        Use AI to calculate relevance score.

        Args:
            opportunity: Opportunity to score

        Returns:
            Score from 0-100
        """
        try:
            prompt = f"""
            Analyze this social media post and determine if it's a good opportunity for a
            construction company that specializes in tile work, bathroom remodeling,
            kitchen remodeling, and general home renovation in the Omaha, Nebraska area.

            Post Title: {opportunity.title or 'N/A'}
            Post Content: {opportunity.content}
            Platform: {opportunity.platform}

            Score from 0-100 where:
            - 90-100: Highly relevant - person is actively looking for services we provide
            - 70-89: Good opportunity - related to our services, worth engaging
            - 50-69: Moderate - might be relevant, needs review
            - 0-49: Low relevance - not a good fit

            Consider:
            1. Is the person actively looking for a contractor/service?
            2. Is it related to tile work, bathroom/kitchen remodel, or flooring?
            3. Is it specific to Omaha or nearby areas?
            4. Is the post a question/request vs just a comment?
            5. Is there urgency or a specific timeline mentioned?

            Respond with ONLY a number from 0-100, nothing else.
            """

            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Extract number from response
            score_match = re.search(r'\d+', response_text)
            if score_match:
                score = int(score_match.group())
                return min(max(score, 0), 100)  # Clamp to 0-100
            else:
                logger.warning(f"Could not parse score from AI response: {response_text}")
                return 50  # Default moderate score

        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            # Fallback to basic keyword scoring
            return len(opportunity.keywords_matched) * 15

    def batch_analyze(
        self,
        opportunities: List[SocialOpportunity]
    ) -> List[SocialOpportunity]:
        """
        Analyze multiple opportunities.

        Args:
            opportunities: List of opportunities to analyze

        Returns:
            List of analyzed opportunities
        """
        logger.info(f"Analyzing {len(opportunities)} opportunities...")

        analyzed = []
        for opp in opportunities:
            try:
                analyzed_opp = self.analyze_opportunity(opp)
                analyzed.append(analyzed_opp)
            except Exception as e:
                logger.error(f"Error analyzing opportunity {opp.platform_id}: {e}")
                analyzed.append(opp)  # Add without analysis

        # Sort by relevance score (highest first)
        analyzed.sort(
            key=lambda x: x.relevance_score if x.relevance_score else 0,
            reverse=True
        )

        logger.info(
            f"Analysis complete. Found {sum(1 for o in analyzed if o.relevance_score and o.relevance_score >= 60)} "
            f"high-relevance opportunities"
        )

        return analyzed

    def filter_relevant(
        self,
        opportunities: List[SocialOpportunity],
        min_score: int = 60,
        require_omaha: bool = True
    ) -> List[SocialOpportunity]:
        """
        Filter opportunities by relevance.

        Args:
            opportunities: List of opportunities
            min_score: Minimum relevance score
            require_omaha: Whether to require Omaha location mentions

        Returns:
            Filtered list
        """
        filtered = []

        for opp in opportunities:
            # Check score
            if opp.relevance_score is None or opp.relevance_score < min_score:
                continue

            # Check location if required
            if require_omaha and not opp.is_omaha_related:
                continue

            filtered.append(opp)

        logger.info(
            f"Filtered {len(opportunities)} opportunities down to "
            f"{len(filtered)} relevant ones (min_score={min_score}, "
            f"require_omaha={require_omaha})"
        )

        return filtered
