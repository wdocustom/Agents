"""
Engagement Manager - Handles posting/commenting on social media with rate limiting.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
import time
import csv
from pathlib import Path

from models.opportunity import SocialOpportunity, OpportunityStatus, Platform
from agents.reddit_monitor import RedditMonitor
from agents.facebook_monitor import FacebookMonitor
from config.settings import get_settings

logger = logging.getLogger(__name__)


class EngagementManager:
    """Manages engagement with social media opportunities."""

    def __init__(self):
        """Initialize the Engagement Manager."""
        self.settings = get_settings()
        self.reddit_monitor = RedditMonitor()
        self.facebook_monitor = FacebookMonitor()

        # Track engagement history
        self.engagement_history: List[dict] = []
        self.load_engagement_history()

    def load_engagement_history(self):
        """Load engagement history from file."""
        history_file = Path("output/engagement_history.csv")

        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.engagement_history = list(reader)
                logger.info(f"Loaded {len(self.engagement_history)} engagement records")
            except Exception as e:
                logger.error(f"Error loading engagement history: {e}")

    def save_engagement_history(self):
        """Save engagement history to file."""
        history_file = Path("output/engagement_history.csv")
        history_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(history_file, 'w', newline='') as f:
                if self.engagement_history:
                    fieldnames = self.engagement_history[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.engagement_history)
            logger.info("Engagement history saved")
        except Exception as e:
            logger.error(f"Error saving engagement history: {e}")

    def can_engage(self) -> tuple[bool, str]:
        """
        Check if we can engage based on rate limits.

        Returns:
            Tuple of (can_engage, reason)
        """
        # Check if auto-engage is enabled
        auto_engage = getattr(self.settings, 'auto_engage', False)
        if not auto_engage:
            return False, "Auto-engage is disabled in settings"

        # Check daily limit
        daily_limit = getattr(self.settings, 'engagement_daily_limit', 10)
        today = datetime.now().date()

        today_engagements = [
            e for e in self.engagement_history
            if datetime.fromisoformat(e['timestamp']).date() == today
        ]

        if len(today_engagements) >= daily_limit:
            return False, f"Daily limit reached ({daily_limit} engagements)"

        # Check minimum delay between engagements
        min_delay = getattr(self.settings, 'engagement_delay_min', 30)

        if self.engagement_history:
            last_engagement = datetime.fromisoformat(
                self.engagement_history[-1]['timestamp']
            )
            time_since_last = datetime.now() - last_engagement

            if time_since_last < timedelta(minutes=min_delay):
                wait_time = (timedelta(minutes=min_delay) - time_since_last).seconds // 60
                return False, f"Must wait {wait_time} more minutes before next engagement"

        return True, "OK"

    def engage_with_opportunity(
        self,
        opportunity: SocialOpportunity,
        dry_run: bool = False
    ) -> bool:
        """
        Engage with an opportunity by posting a response.

        Args:
            opportunity: SocialOpportunity to engage with
            dry_run: If True, don't actually post (for testing)

        Returns:
            True if successful, False otherwise
        """
        # Check if we can engage
        can_engage, reason = self.can_engage()
        if not can_engage and not dry_run:
            logger.warning(f"Cannot engage: {reason}")
            return False

        # Check if we have a response
        if not opportunity.suggested_response:
            logger.error("No suggested response available")
            return False

        logger.info(f"Engaging with opportunity: {opportunity.url}")

        if dry_run:
            logger.info("[DRY RUN] Would post:")
            logger.info(f"  Platform: {opportunity.platform}")
            logger.info(f"  URL: {opportunity.url}")
            logger.info(f"  Response: {opportunity.suggested_response}")
            return True

        # Post the response
        success = False

        try:
            if opportunity.platform == Platform.REDDIT:
                success = self.reddit_monitor.post_comment(
                    opportunity.platform_id,
                    opportunity.suggested_response
                )
            elif opportunity.platform == Platform.FACEBOOK:
                logger.warning("Facebook engagement not implemented")
                success = False
            else:
                logger.error(f"Unknown platform: {opportunity.platform}")
                success = False

            if success:
                # Record engagement
                self._record_engagement(opportunity)
                opportunity.status = OpportunityStatus.ENGAGED
                opportunity.engaged_at = datetime.now()

                logger.info(f"Successfully engaged with {opportunity.platform_id}")
            else:
                logger.error(f"Failed to engage with {opportunity.platform_id}")

        except Exception as e:
            logger.error(f"Error engaging with opportunity: {e}")
            success = False

        return success

    def _record_engagement(self, opportunity: SocialOpportunity):
        """
        Record an engagement in history.

        Args:
            opportunity: SocialOpportunity that was engaged with
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'platform': opportunity.platform,
            'platform_id': opportunity.platform_id,
            'url': opportunity.url,
            'response_preview': opportunity.suggested_response[:100] + '...',
            'relevance_score': opportunity.relevance_score or 0,
        }

        self.engagement_history.append(record)
        self.save_engagement_history()

    def batch_engage(
        self,
        opportunities: List[SocialOpportunity],
        max_engagements: Optional[int] = None,
        dry_run: bool = False
    ) -> int:
        """
        Engage with multiple opportunities.

        Args:
            opportunities: List of opportunities
            max_engagements: Maximum number to engage with (None = no limit)
            dry_run: If True, don't actually post

        Returns:
            Number of successful engagements
        """
        if max_engagements is None:
            max_engagements = len(opportunities)

        successful = 0
        delay_min = getattr(self.settings, 'engagement_delay_min', 30)

        for i, opp in enumerate(opportunities):
            if successful >= max_engagements:
                logger.info(f"Reached max engagements limit ({max_engagements})")
                break

            # Only engage with high-quality, unengaged opportunities
            if not opp.should_engage():
                logger.debug(f"Skipping opportunity {opp.platform_id} (should_engage=False)")
                continue

            # Attempt engagement
            if self.engage_with_opportunity(opp, dry_run=dry_run):
                successful += 1

                # Wait between engagements (except for dry run)
                if not dry_run and i < len(opportunities) - 1:
                    wait_seconds = delay_min * 60
                    logger.info(f"Waiting {delay_min} minutes before next engagement...")
                    time.sleep(wait_seconds)

        logger.info(f"Batch engagement complete: {successful} successful out of {len(opportunities)}")
        return successful

    def get_engagement_stats(self) -> dict:
        """
        Get statistics about engagements.

        Returns:
            Dictionary with engagement statistics
        """
        today = datetime.now().date()

        today_engagements = [
            e for e in self.engagement_history
            if datetime.fromisoformat(e['timestamp']).date() == today
        ]

        this_week = datetime.now() - timedelta(days=7)
        week_engagements = [
            e for e in self.engagement_history
            if datetime.fromisoformat(e['timestamp']) >= this_week
        ]

        return {
            'total_engagements': len(self.engagement_history),
            'today_engagements': len(today_engagements),
            'week_engagements': len(week_engagements),
            'daily_limit': getattr(self.settings, 'engagement_daily_limit', 10),
            'remaining_today': max(
                0,
                getattr(self.settings, 'engagement_daily_limit', 10) - len(today_engagements)
            ),
            'last_engagement': (
                self.engagement_history[-1]['timestamp']
                if self.engagement_history else None
            ),
        }

    def export_opportunities(
        self,
        opportunities: List[SocialOpportunity],
        filename: Optional[str] = None
    ) -> str:
        """
        Export opportunities to CSV file.

        Args:
            opportunities: List of opportunities to export
            filename: Optional filename

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"opportunities_{timestamp}.csv"

        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if opportunities:
                    fieldnames = list(opportunities[0].to_csv_row().keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for opp in opportunities:
                        writer.writerow(opp.to_csv_row())

            logger.info(f"Exported {len(opportunities)} opportunities to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting opportunities: {e}")
            raise
