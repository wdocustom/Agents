"""
Simple Reddit scraper - no authentication required!
Uses web scraping to find construction service requests.
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional
import time
import re

from models.opportunity import SocialOpportunity, Platform

logger = logging.getLogger(__name__)


class SimpleRedditScraper:
    """Scrapes Reddit without requiring API credentials."""

    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info("Simple Reddit scraper initialized (no credentials needed)")

    def get_subreddits(self) -> List[str]:
        """Get list of subreddits to monitor."""
        return [
            'Omaha',
            'Nebraska',
            'HomeImprovement',
            'DIY',
            'homeowners',
            'Renovations',
            'Tile',
            'Flooring',
        ]

    def scrape_subreddit(self, subreddit: str, limit: int = 25) -> List[SocialOpportunity]:
        """
        Scrape a subreddit for recent posts.

        Args:
            subreddit: Subreddit name
            limit: Max posts to retrieve

        Returns:
            List of opportunities
        """
        opportunities = []

        try:
            # Use old.reddit.com for easier scraping
            url = f"https://old.reddit.com/r/{subreddit}/new"

            logger.info(f"Scraping r/{subreddit}...")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all post containers
            posts = soup.find_all('div', class_='thing', limit=limit)

            for post in posts:
                try:
                    opp = self._parse_post(post, subreddit)
                    if opp:
                        opportunities.append(opp)
                except Exception as e:
                    logger.debug(f"Error parsing post: {e}")
                    continue

            logger.info(f"Found {len(opportunities)} posts in r/{subreddit}")

            # Be nice to Reddit's servers
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping r/{subreddit}: {e}")

        return opportunities

    def _parse_post(self, post_element, subreddit: str) -> Optional[SocialOpportunity]:
        """Parse a post element into a SocialOpportunity."""
        try:
            # Extract post ID
            post_id = post_element.get('data-fullname', '').replace('t3_', '')
            if not post_id:
                return None

            # Extract title
            title_element = post_element.find('a', class_='title')
            if not title_element:
                return None
            title = title_element.text.strip()

            # Extract URL
            permalink = post_element.get('data-permalink', '')
            url = f"https://reddit.com{permalink}" if permalink else None

            # Extract author
            author_element = post_element.find('a', class_='author')
            author = author_element.text if author_element else 'unknown'

            # Extract timestamp
            time_element = post_element.find('time')
            if time_element:
                timestamp_str = time_element.get('datetime')
                created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                created_at = datetime.now()

            # Extract score
            score_element = post_element.find('div', class_='score')
            if score_element:
                score_text = score_element.get('title', '0')
                try:
                    score = int(score_text)
                except:
                    score = 0
            else:
                score = 0

            # Extract comment count
            comments_element = post_element.find('a', class_='comments')
            if comments_element:
                comments_text = comments_element.text
                num_comments_match = re.search(r'(\d+)', comments_text)
                num_comments = int(num_comments_match.group(1)) if num_comments_match else 0
            else:
                num_comments = 0

            # Get post content (for self posts)
            content = ""
            expando = post_element.find('div', class_='expando')
            if expando:
                usertext = expando.find('div', class_='usertext-body')
                if usertext:
                    content = usertext.get_text(strip=True)

            # Create opportunity
            opportunity = SocialOpportunity(
                platform=Platform.REDDIT,
                platform_id=post_id,
                url=url or '',
                author=author,
                title=title,
                content=content,
                full_text=f"{title}\n\n{content}".strip(),
                created_at=created_at,
                subreddit=subreddit,
                num_comments=num_comments,
                score=score,
            )

            return opportunity

        except Exception as e:
            logger.debug(f"Error parsing post element: {e}")
            return None

    def monitor_all(self, hours_back: int = 24, limit_per_sub: int = 25) -> List[SocialOpportunity]:
        """
        Monitor all subreddits.

        Args:
            hours_back: How many hours back to check
            limit_per_sub: Max posts per subreddit

        Returns:
            Combined list of opportunities
        """
        all_opportunities = []
        subreddits = self.get_subreddits()
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        logger.info(f"Monitoring {len(subreddits)} subreddits (web scraping mode)...")

        for subreddit in subreddits:
            try:
                opportunities = self.scrape_subreddit(subreddit, limit=limit_per_sub)

                # Filter by time
                recent_opps = [
                    opp for opp in opportunities
                    if opp.created_at >= cutoff_time
                ]

                all_opportunities.extend(recent_opps)

            except Exception as e:
                logger.error(f"Error monitoring r/{subreddit}: {e}")

        logger.info(f"Total opportunities found: {len(all_opportunities)}")
        return all_opportunities
