"""
Reddit Monitoring Agent - Monitors subreddits for construction service requests.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import praw
from praw.models import Submission, Comment

from models.opportunity import SocialOpportunity, Platform
from config.settings import get_settings

logger = logging.getLogger(__name__)


class RedditMonitor:
    """Agent that monitors Reddit for construction service requests."""

    def __init__(self):
        """Initialize the Reddit Monitor."""
        self.settings = get_settings()

        # Initialize Reddit API client
        try:
            self.reddit = praw.Reddit(
                client_id=self.settings.reddit_client_id,
                client_secret=self.settings.reddit_client_secret,
                username=self.settings.reddit_username,
                password=self.settings.reddit_password,
                user_agent=f"construction_lead_bot/1.0 (by u/{self.settings.reddit_username})"
            )
            self.authenticated = True
            logger.info("Reddit API authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to authenticate with Reddit API: {e}")
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

        # Add custom subreddits from settings if configured
        if hasattr(self.settings, 'custom_subreddits'):
            subreddits.extend(self.settings.custom_subreddits)

        return subreddits

    def monitor_new_posts(
        self,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[SocialOpportunity]:
        """
        Monitor subreddits for new posts.

        Args:
            hours_back: How many hours back to check
            limit: Maximum number of posts per subreddit

        Returns:
            List of potential opportunities
        """
        if not self.authenticated:
            logger.error("Reddit API not authenticated, cannot monitor")
            return []

        opportunities = []
        subreddits = self.get_subreddits()
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        logger.info(f"Monitoring {len(subreddits)} subreddits for new posts...")

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

    def search_posts(
        self,
        query: str,
        time_filter: str = 'week',
        limit: int = 50
    ) -> List[SocialOpportunity]:
        """
        Search Reddit for specific keywords.

        Args:
            query: Search query
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum results

        Returns:
            List of opportunities
        """
        if not self.authenticated:
            logger.error("Reddit API not authenticated")
            return []

        opportunities = []
        subreddits = self.get_subreddits()

        logger.info(f"Searching Reddit for: '{query}'")

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                for submission in subreddit.search(
                    query,
                    time_filter=time_filter,
                    limit=limit
                ):
                    opportunity = self._submission_to_opportunity(submission)
                    if opportunity:
                        opportunities.append(opportunity)

            except Exception as e:
                logger.error(f"Error searching r/{subreddit_name}: {e}")

        logger.info(f"Found {len(opportunities)} opportunities for query '{query}'")
        return opportunities

    def _submission_to_opportunity(
        self,
        submission: Submission
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

    def post_comment(
        self,
        submission_id: str,
        comment_text: str
    ) -> bool:
        """
        Post a comment on a Reddit submission.

        Args:
            submission_id: Reddit submission ID
            comment_text: Comment text to post

        Returns:
            True if successful, False otherwise
        """
        if not self.authenticated:
            logger.error("Cannot post comment: Not authenticated")
            return False

        try:
            submission = self.reddit.submission(id=submission_id)
            comment = submission.reply(comment_text)

            logger.info(f"Posted comment on submission {submission_id}")
            logger.debug(f"Comment permalink: {comment.permalink}")

            return True

        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return False

    def get_post_details(self, submission_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific post.

        Args:
            submission_id: Reddit submission ID

        Returns:
            Dictionary with post details or None
        """
        if not self.authenticated:
            return None

        try:
            submission = self.reddit.submission(id=submission_id)

            return {
                'title': submission.title,
                'author': str(submission.author) if submission.author else "[deleted]",
                'content': submission.selftext,
                'url': f"https://reddit.com{submission.permalink}",
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': submission.created_utc,
                'subreddit': submission.subreddit.display_name,
            }

        except Exception as e:
            logger.error(f"Error getting post details: {e}")
            return None

    def monitor_keywords(
        self,
        keywords: List[str],
        hours_back: int = 24
    ) -> List[SocialOpportunity]:
        """
        Monitor for posts containing specific keywords.

        Args:
            keywords: List of keywords to search for
            hours_back: How many hours back to search

        Returns:
            List of opportunities
        """
        all_opportunities = []

        for keyword in keywords:
            opportunities = self.search_posts(
                query=keyword,
                time_filter='day' if hours_back <= 24 else 'week',
                limit=50
            )
            all_opportunities.extend(opportunities)

        # Remove duplicates by submission ID
        unique_opps = {}
        for opp in all_opportunities:
            if opp.platform_id not in unique_opps:
                unique_opps[opp.platform_id] = opp

        return list(unique_opps.values())
