"""
Web search tools for finding construction leads.
"""

import os
import json
import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for searching the web for construction leads."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize web search tool.

        Args:
            api_key: Serper API key for Google search
        """
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def search_google(
        self,
        query: str,
        num_results: int = 10,
        location: str = "Omaha, Nebraska"
    ) -> List[Dict]:
        """
        Search Google using Serper API.

        Args:
            query: Search query
            num_results: Number of results to return
            location: Geographic location for search

        Returns:
            List of search results
        """
        if not self.api_key:
            logger.warning("No Serper API key provided, using fallback search")
            return self._fallback_search(query)

        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'q': query,
            'num': num_results,
            'location': location,
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('organic', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'google_search'
                })

            return results

        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> List[Dict]:
        """
        Fallback search method when API is unavailable.

        Args:
            query: Search query

        Returns:
            List of search results (limited)
        """
        # Return predefined search targets for construction leads
        logger.info(f"Using fallback search for: {query}")

        # These are real data sources for construction leads in Omaha
        fallback_results = [
            {
                'title': 'City of Omaha Building Permits',
                'link': 'https://www.cityofomaha.org/government/departments/planning/building-permits',
                'snippet': 'Search and view building permits issued by the City of Omaha.',
                'source': 'fallback'
            },
            {
                'title': 'Douglas County Building Permits',
                'link': 'https://www.douglascounty-ne.gov/planning',
                'snippet': 'Building and construction permits for Douglas County, NE.',
                'source': 'fallback'
            },
            {
                'title': 'Omaha Commercial Real Estate Development',
                'link': 'https://www.selectomaha.com/',
                'snippet': 'Greater Omaha Chamber - Economic development and new construction projects.',
                'source': 'fallback'
            },
        ]

        return fallback_results

    def search_construction_leads(
        self,
        area: str = "Omaha, Nebraska",
        project_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for construction leads in specified area.

        Args:
            area: Geographic area to search
            project_types: Types of construction projects to search for

        Returns:
            List of search results
        """
        if project_types is None:
            project_types = [
                "commercial construction",
                "new building development",
                "renovation project",
                "industrial construction"
            ]

        all_results = []

        # Search queries targeting construction leads
        queries = [
            f"{area} building permits issued",
            f"{area} commercial construction projects",
            f"{area} new development projects",
            f"{area} construction bids opportunities",
            f"{area} commercial real estate development",
        ]

        for query in queries:
            try:
                results = self.search_google(query, num_results=5, location=area)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Search failed for '{query}': {e}")

        return all_results

    @staticmethod
    def extract_page_content(url: str) -> Optional[str]:
        """
        Extract text content from a web page.

        Args:
            url: URL to extract content from

        Returns:
            Extracted text content or None
        """
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text[:5000]  # Limit to first 5000 chars

        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return None
