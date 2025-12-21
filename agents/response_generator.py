"""
Response Generator Agent - Creates personalized responses for social media opportunities.
"""

import logging
from typing import Optional
from anthropic import Anthropic

from models.opportunity import SocialOpportunity
from config.settings import get_settings

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Agent that generates personalized responses to social media posts."""

    def __init__(self):
        """Initialize the Response Generator."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)

    def generate_response(
        self,
        opportunity: SocialOpportunity,
        tone: str = "professional_friendly"
    ) -> str:
        """
        Generate a personalized response for an opportunity.

        Args:
            opportunity: SocialOpportunity to respond to
            tone: Response tone (professional_friendly, casual, expert)

        Returns:
            Generated response text
        """
        try:
            prompt = self._build_response_prompt(opportunity, tone)

            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()

            logger.info(f"Generated response for opportunity {opportunity.platform_id}")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(opportunity)

    def _build_response_prompt(
        self,
        opportunity: SocialOpportunity,
        tone: str
    ) -> str:
        """
        Build the prompt for response generation.

        Args:
            opportunity: SocialOpportunity
            tone: Response tone

        Returns:
            Prompt string
        """
        # Get business info from settings
        business_name = getattr(self.settings, 'business_name', 'our construction company')
        services = getattr(self.settings, 'services', 'tile work and remodeling')
        phone = getattr(self.settings, 'business_phone', '')
        website = getattr(self.settings, 'business_website', '')

        tone_guidance = {
            'professional_friendly': 'professional but friendly and approachable',
            'casual': 'casual and conversational, like talking to a neighbor',
            'expert': 'professional and expert, emphasizing experience and quality'
        }.get(tone, 'professional but friendly')

        prompt = f"""
        You are writing a response to a social media post on {opportunity.platform.upper()}.
        The person is looking for construction/remodeling services in Omaha, NE.

        POST DETAILS:
        Title: {opportunity.title or 'N/A'}
        Content: {opportunity.content}
        Platform: {opportunity.platform} {f'(r/{opportunity.subreddit})' if opportunity.subreddit else ''}

        YOUR BUSINESS:
        Name: {business_name}
        Services: {services}
        {f'Phone: {phone}' if phone else ''}
        {f'Website: {website}' if website else ''}

        INSTRUCTIONS:
        1. Write a {tone_guidance} response
        2. Be helpful and genuine - don't be overly salesy
        3. Address their specific needs mentioned in the post
        4. Keep it concise (2-4 sentences)
        5. Mention relevant experience if applicable
        6. Provide contact info naturally
        7. Do NOT use emojis
        8. Do NOT use hashtags
        9. Sound like a real person, not a bot
        10. If on Reddit, match the casual Reddit tone
        11. Offer value before asking for business

        IMPORTANT:
        - Don't spam or oversell
        - Be respectful of community guidelines
        - Provide genuine help
        - Only mention services that are actually relevant

        Write the response now (just the response text, no other commentary):
        """

        return prompt

    def _get_fallback_response(
        self,
        opportunity: SocialOpportunity
    ) -> str:
        """
        Get a fallback response if AI generation fails.

        Args:
            opportunity: SocialOpportunity

        Returns:
            Fallback response text
        """
        business_name = getattr(self.settings, 'business_name', 'our company')
        phone = getattr(self.settings, 'business_phone', '')

        # Simple template response
        if "tile" in opportunity.content.lower():
            service = "tile work"
        elif "bathroom" in opportunity.content.lower():
            service = "bathroom remodels"
        elif "kitchen" in opportunity.content.lower():
            service = "kitchen renovations"
        else:
            service = "remodeling projects"

        response = (
            f"Hi! I specialize in {service} in the Omaha area and would be happy to help. "
            f"Feel free to reach out if you'd like to discuss your project"
        )

        if phone:
            response += f" at {phone}"

        response += "."

        return response

    def batch_generate(
        self,
        opportunities: list[SocialOpportunity],
        tone: str = "professional_friendly"
    ) -> list[SocialOpportunity]:
        """
        Generate responses for multiple opportunities.

        Args:
            opportunities: List of opportunities
            tone: Response tone

        Returns:
            Opportunities with suggested_response filled in
        """
        logger.info(f"Generating responses for {len(opportunities)} opportunities...")

        for opp in opportunities:
            if opp.suggested_response is None:
                try:
                    opp.suggested_response = self.generate_response(opp, tone)
                except Exception as e:
                    logger.error(f"Error generating response for {opp.platform_id}: {e}")

        logger.info("Response generation complete")
        return opportunities

    def customize_response(
        self,
        base_response: str,
        customization: str
    ) -> str:
        """
        Customize a response with additional instructions.

        Args:
            base_response: Original response
            customization: Customization instructions

        Returns:
            Customized response
        """
        try:
            prompt = f"""
            Take this response and modify it according to the customization instructions:

            ORIGINAL RESPONSE:
            {base_response}

            CUSTOMIZATION INSTRUCTIONS:
            {customization}

            Write the modified response (just the response text, no commentary):
            """

            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()

        except Exception as e:
            logger.error(f"Error customizing response: {e}")
            return base_response

    def get_response_variations(
        self,
        opportunity: SocialOpportunity,
        count: int = 3
    ) -> list[str]:
        """
        Generate multiple response variations.

        Args:
            opportunity: SocialOpportunity
            count: Number of variations to generate

        Returns:
            List of response variations
        """
        variations = []

        tones = ['professional_friendly', 'casual', 'expert']

        for i in range(min(count, len(tones))):
            try:
                response = self.generate_response(opportunity, tones[i])
                variations.append(response)
            except Exception as e:
                logger.error(f"Error generating variation {i+1}: {e}")

        return variations
