"""
Reddit Monitoring Agent - Read-only version (no credentials needed for monitoring).
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import praw

from models.opportunity import SocialOpportunity, Platform
from config.settings import get_settings

logger = logging.getLogger(__name__)


class RedditMonitorReadOnly:
    """Agent that monitors Reddit for construction service requests (read-only, no auth needed)."""

    def __init__(self):
        """Initialize the Reddit Monitor in read-only mode."""
        self.settings = get_settings()

        # Initialize Reddit API client in READ-ONLY mode (no credentials needed!)
        try:
            self.reddit = praw.Reddit(
                client_id="reddit_monitor_readonly",
                client_secret="",
                user_agent="construction_lead_monitor/1.0 (read-only mode)"
            )
            # Test connection
            test_sub = self.reddit.subreddit("Omaha")
            _ = test_sub.display_name
            self.authenticated = True
            logger.info("Reddit read-only mode initialized successfully (no auth required)")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit in read-only mode: {e}")
            self.authenticated = False

    def get_subreddits(self) -> List[str]:
        """
        Get list of subreddits to monitor.

        Returns:
            List of subreddit names
        """
        # Default subreddits for Omaha and home improvement
        subreddits = [
            'Omaha',
            'Nebraska',
            'HomeImprovement',
            'DIY',
            'homeowners',
            'Renovations',
            'Tile',
            'Flooring',
            'Bathroom',
            'Kitchen',
            'Construction',
            'Remodeling',
            'HomeRenovation',
        ]

        return subreddits

    def monitor_new_posts(
        self,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[SocialOpportunity]:
        """
        Monitor subreddits for new posts (READ-ONLY).

        Args:
            hours_back: How many hours back to check
            limit: Maximum number of posts per subreddit

        Returns:
            List of potential opportunities
        """
        if not self.authenticated:
            logger.error("Reddit not initialized, cannot monitor")
            return []

        opportunities = []
        subreddits = self.get_subreddits()
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        logger.info(f"Monitoring {len(subreddits)} subreddits (READ-ONLY MODE)...")

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Check new posts
                for submission in subreddit.new(limit=limit):
                    post_time = datetime.fromtimestamp(submission.created_utc)

                    # Skip old posts
                    if post_time < cutoff_time:
                        continue

                    # Create opportunity object
                    opportunity = self._submission_to_opportunity(submission)
                    if opportunity:
                        opportunities.append(opportunity)
                        logger.info(
                            f"Found opportunity in r/{subreddit_name}: {submission.title[:60]}..."
                        )

            except Exception as e:
                logger.error(f"Error monitoring r/{subreddit_name}: {e}")

        logger.info(f"Found {len(opportunities)} potential opportunities on Reddit")
        return opportunities

    def _submission_to_opportunity(
        self,
        submission
    ) -> Optional[SocialOpportunity]:
        """
        Convert Reddit submission to SocialOpportunity.

        Args:
            submission: Reddit submission object

        Returns:
            SocialOpportunity or None
        """
        try:
            # Get post content
            title = submission.title
            content = submission.selftext if submission.is_self else ""
            full_text = f"{title}\n\n{content}".strip()

            # Create opportunity
            opportunity = SocialOpportunity(
                platform=Platform.REDDIT,
                platform_id=submission.id,
                url=f"https://reddit.com{submission.permalink}",
                author=str(submission.author) if submission.author else "[deleted]",
                title=title,
                content=content,
                full_text=full_text,
                created_at=datetime.fromtimestamp(submission.created_utc),
                subreddit=submission.subreddit.display_name,
                num_comments=submission.num_comments,
                score=submission.score,
                raw_data={
                    'upvote_ratio': submission.upvote_ratio,
                    'is_self': submission.is_self,
                    'link_flair_text': submission.link_flair_text,
                }
            )

            return opportunity

        except Exception as e:
            logger.error(f"Error converting submission to opportunity: {e}")
            return None
