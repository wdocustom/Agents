"""
Social Media Lead Orchestrator - Coordinates social media monitoring agents.
"""

import logging
from typing import List, Optional
from datetime import datetime
import time

from models.opportunity import SocialOpportunity
from agents.reddit_monitor import RedditMonitor
from agents.facebook_monitor import FacebookMonitor
from agents.keyword_detector import KeywordDetector
from agents.response_generator import ResponseGenerator
from agents.engagement_manager import EngagementManager
from config.settings import get_settings

logger = logging.getLogger(__name__)


class SocialMediaOrchestrator:
    """Orchestrates social media monitoring and engagement."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.settings = get_settings()

        # Initialize agents
        self.reddit_monitor = RedditMonitor()
        self.facebook_monitor = FacebookMonitor()
        self.keyword_detector = KeywordDetector()
        self.response_generator = ResponseGenerator()
        self.engagement_manager = EngagementManager()

        # Storage
        self.opportunities: List[SocialOpportunity] = []
        self.relevant_opportunities: List[SocialOpportunity] = []

        logger.info("Social media orchestrator initialized")

    def monitor(
        self,
        platforms: List[str] = ['reddit'],
        hours_back: int = 24,
        auto_engage: bool = False
    ) -> List[SocialOpportunity]:
        """
        Monitor social media platforms for opportunities.

        Args:
            platforms: List of platforms to monitor ('reddit', 'facebook')
            hours_back: How many hours back to search
            auto_engage: Whether to automatically engage

        Returns:
            List of relevant opportunities
        """
        logger.info("="*70)
        logger.info("STARTING SOCIAL MEDIA MONITORING")
        logger.info("="*70)
        logger.info(f"Platforms: {', '.join(platforms)}")
        logger.info(f"Lookback: {hours_back} hours")
        logger.info(f"Auto-engage: {auto_engage}")
        logger.info("="*70)

        start_time = datetime.now()

        try:
            # Step 1: Collect opportunities from platforms
            logger.info("\n[STEP 1/5] Collecting opportunities from platforms...")
            self.opportunities = self._collect_opportunities(platforms, hours_back)
            logger.info(f"✓ Found {len(self.opportunities)} total opportunities")

            # Step 2: Analyze and filter
            logger.info("\n[STEP 2/5] Analyzing and filtering opportunities...")
            analyzed_opportunities = self.keyword_detector.batch_analyze(self.opportunities)
            self.relevant_opportunities = self.keyword_detector.filter_relevant(
                analyzed_opportunities,
                min_score=self.settings.min_lead_score,
                require_omaha=True
            )
            logger.info(f"✓ {len(self.relevant_opportunities)} relevant opportunities found")

            # Step 3: Generate responses
            if self.relevant_opportunities:
                logger.info("\n[STEP 3/5] Generating responses...")
                self.response_generator.batch_generate(self.relevant_opportunities)
                logger.info("✓ Responses generated")
            else:
                logger.info("\n[STEP 3/5] No relevant opportunities, skipping response generation")

            # Step 4: Auto-engage if enabled
            if auto_engage and self.relevant_opportunities:
                logger.info("\n[STEP 4/5] Engaging with opportunities...")
                engaged_count = self.engagement_manager.batch_engage(
                    self.relevant_opportunities,
                    max_engagements=self.settings.engagement_daily_limit
                )
                logger.info(f"✓ Engaged with {engaged_count} opportunities")
            else:
                logger.info("\n[STEP 4/5] Auto-engage disabled, skipping engagement")

            # Step 5: Export results
            logger.info("\n[STEP 5/5] Exporting results...")
            if self.relevant_opportunities:
                output_file = self.engagement_manager.export_opportunities(
                    self.relevant_opportunities
                )
                logger.info(f"✓ Results saved to: {output_file}")
            else:
                logger.info("No opportunities to export")

            # Summary
            duration = (datetime.now() - start_time).total_seconds()
            self._print_summary(duration, auto_engage)

            return self.relevant_opportunities

        except Exception as e:
            logger.error(f"Monitoring failed: {e}", exc_info=True)
            raise

    def _collect_opportunities(
        self,
        platforms: List[str],
        hours_back: int
    ) -> List[SocialOpportunity]:
        """
        Collect opportunities from all platforms.

        Args:
            platforms: List of platform names
            hours_back: Hours back to search

        Returns:
            Combined list of opportunities
        """
        all_opportunities = []

        if 'reddit' in platforms:
            logger.info("Monitoring Reddit...")
            reddit_opps = self.reddit_monitor.monitor_new_posts(
                hours_back=hours_back,
                limit=100
            )
            all_opportunities.extend(reddit_opps)
            logger.info(f"  Found {len(reddit_opps)} Reddit opportunities")

        if 'facebook' in platforms:
            logger.info("Monitoring Facebook...")
            fb_opps = self.facebook_monitor.monitor_groups(hours_back=hours_back)
            all_opportunities.extend(fb_opps)
            logger.info(f"  Found {len(fb_opps)} Facebook opportunities")

        return all_opportunities

    def _print_summary(self, duration: float, auto_engage: bool):
        """
        Print summary of monitoring results.

        Args:
            duration: Duration in seconds
            auto_engage: Whether auto-engage was enabled
        """
        logger.info("\n" + "="*70)
        logger.info("MONITORING SUMMARY")
        logger.info("="*70)
        logger.info(f"Total opportunities found: {len(self.opportunities)}")
        logger.info(f"Relevant opportunities: {len(self.relevant_opportunities)}")
        logger.info(
            f"Relevance rate: "
            f"{len(self.relevant_opportunities)/len(self.opportunities)*100:.1f}%"
            if self.opportunities else "0%"
        )
        logger.info(f"Duration: {duration:.1f} seconds")

        if auto_engage:
            stats = self.engagement_manager.get_engagement_stats()
            logger.info(f"Engagements today: {stats['today_engagements']}")
            logger.info(f"Remaining today: {stats['remaining_today']}")

        logger.info("="*70)

        if self.relevant_opportunities:
            logger.info("\nTOP OPPORTUNITIES:")
            logger.info("-"*70)

            # Show top 5
            for i, opp in enumerate(self.relevant_opportunities[:5], 1):
                logger.info(f"\n{i}. [{opp.platform.upper()}] {opp.title or 'Untitled'}")
                logger.info(f"   Score: {opp.relevance_score}/100")
                logger.info(f"   URL: {opp.url}")
                logger.info(f"   Content: {opp.content[:100]}...")
                if opp.keywords_matched:
                    logger.info(f"   Keywords: {', '.join(opp.keywords_matched[:5])}")

        logger.info("\n" + "="*70)

    def run_continuous(
        self,
        platforms: List[str] = ['reddit'],
        interval_minutes: int = 15,
        auto_engage: bool = False
    ):
        """
        Run continuous monitoring with periodic checks.

        Args:
            platforms: Platforms to monitor
            interval_minutes: Minutes between checks
            auto_engage: Whether to auto-engage
        """
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")

        run_count = 0

        try:
            while True:
                run_count += 1
                logger.info(f"\n{'='*70}")
                logger.info(f"MONITORING RUN #{run_count}")
                logger.info(f"{'='*70}\n")

                # Run monitoring
                self.monitor(
                    platforms=platforms,
                    hours_back=interval_minutes // 60 + 1,  # Slightly overlap
                    auto_engage=auto_engage
                )

                # Wait before next run
                logger.info(f"\nWaiting {interval_minutes} minutes until next check...")
                logger.info(f"Next run at: {(datetime.now() + timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')}")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logger.info("\n\nMonitoring stopped by user")
        except Exception as e:
            logger.error(f"Continuous monitoring error: {e}", exc_info=True)
            raise

    def get_statistics(self) -> dict:
        """
        Get statistics about monitoring.

        Returns:
            Dictionary of statistics
        """
        relevant_scores = [
            opp.relevance_score
            for opp in self.relevant_opportunities
            if opp.relevance_score is not None
        ]

        stats = {
            'total_opportunities': len(self.opportunities),
            'relevant_opportunities': len(self.relevant_opportunities),
            'relevance_rate': (
                len(self.relevant_opportunities) / len(self.opportunities)
                if self.opportunities else 0
            ),
            'average_relevance_score': (
                sum(relevant_scores) / len(relevant_scores)
                if relevant_scores else 0
            ),
            'high_priority_count': sum(1 for o in self.relevant_opportunities if o.is_high_priority()),
        }

        # Add engagement stats
        stats.update(self.engagement_manager.get_engagement_stats())

        return stats


# Import timedelta for continuous mode
from datetime import timedelta
