"""
Craigslist scraper for services wanted in Omaha area.
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


class CraigslistScraper:
    """Scrapes Craigslist for service requests."""

    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://omaha.craigslist.org"
        logger.info("Craigslist scraper initialized")

    def scrape_services_wanted(self, limit=50):
        """
        Scrape services wanted section.

        Args:
            limit: Max posts to retrieve

        Returns:
            List of opportunities
        """
        opportunities = []

        try:
            # Services wanted in Omaha
            url = f"{self.base_url}/search/swg"  # swg = services wanted - general

            logger.info("Scraping Craigslist services wanted...")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all post listings
            posts = soup.find_all('li', class_='cl-static-search-result', limit=limit)

            for post in posts:
                try:
                    opp = self._parse_post(post)
                    if opp:
                        opportunities.append(opp)
                except Exception as e:
                    logger.debug(f"Error parsing post: {e}")
                    continue

            logger.info(f"Found {len(opportunities)} Craigslist posts")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")

        return opportunities

    def _parse_post(self, post_element):
        """Parse a Craigslist post element."""
        try:
            # Get title and link
            title_element = post_element.find('a', class_='posting-title')
            if not title_element:
                return None

            title = title_element.text.strip()
            url = title_element.get('href', '')
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Extract post ID from URL
            post_id_match = re.search(r'/(\d+)\.html', url)
            post_id = post_id_match.group(1) if post_id_match else str(hash(url))

            # Get location
            location_element = post_element.find('div', class_='location')
            location = location_element.text.strip() if location_element else 'Omaha'

            # Get posted time
            time_element = post_element.find('div', class_='meta')
            created_at = datetime.now()
            if time_element:
                time_text = time_element.text
                # Parse relative time like "2h ago", "3d ago"
                if 'min' in time_text or 'hour' in time_text or 'h' in time_text:
                    created_at = datetime.now()
                elif 'd' in time_text or 'day' in time_text:
                    days_match = re.search(r'(\d+)', time_text)
                    if days_match:
                        days = int(days_match.group(1))
                        created_at = datetime.now() - timedelta(days=days)

            # Try to get post content (requires clicking into post)
            content = self._get_post_content(url)

            opportunity = SocialOpportunity(
                platform=Platform.OTHER,
                platform_id=post_id,
                url=url,
                author='Craigslist User',
                title=title,
                content=content,
                full_text=f"{title}\n\n{content}".strip(),
                created_at=created_at,
                group_name=f"Craigslist Omaha - Services Wanted ({location})",
            )

            return opportunity

        except Exception as e:
            logger.debug(f"Error parsing Craigslist post: {e}")
            return None

    def _get_post_content(self, url):
        """Get the full content of a Craigslist post."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find post body
            body = soup.find('section', id='postingbody')
            if body:
                # Remove QR code text
                for qr in body.find_all('div', class_='print-qrcode-container'):
                    qr.decompose()
                return body.get_text(strip=True)[:500]  # Limit to 500 chars

            return ""

        except Exception as e:
            logger.debug(f"Error getting post content: {e}")
            return ""

    def scrape_housing_wanted(self, limit=25):
        """Scrape housing wanted (sometimes has remodeling requests)."""
        opportunities = []

        try:
            url = f"{self.base_url}/search/hsw"  # housing wanted

            logger.info("Scraping Craigslist housing wanted...")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('li', class_='cl-static-search-result', limit=limit)

            for post in posts:
                try:
                    opp = self._parse_post(post)
                    if opp and ('remodel' in opp.full_text.lower() or
                               'renovation' in opp.full_text.lower() or
                               'contractor' in opp.full_text.lower()):
                        opportunities.append(opp)
                except Exception as e:
                    logger.debug(f"Error parsing post: {e}")
                    continue

            logger.info(f"Found {len(opportunities)} relevant housing posts")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping Craigslist housing: {e}")

        return opportunities

    def monitor_all(self):
        """Monitor all Craigslist sections."""
        all_opportunities = []

        # Services wanted
        all_opportunities.extend(self.scrape_services_wanted(limit=50))

        # Housing wanted (filtered for construction-related)
        all_opportunities.extend(self.scrape_housing_wanted(limit=25))

        logger.info(f"Total Craigslist opportunities: {len(all_opportunities)}")
        return all_opportunities
