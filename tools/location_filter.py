"""
Location-based filtering and geocoding tools.
"""

import math
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class LocationFilter:
    """Handles location-based filtering and geocoding."""

    def __init__(self, target_lat: float, target_lon: float, radius_miles: float = 35.0):
        """
        Initialize location filter.

        Args:
            target_lat: Target latitude (Omaha: 41.2565)
            target_lon: Target longitude (Omaha: -95.9345)
            radius_miles: Search radius in miles (default: 35)
        """
        self.target_coords = (target_lat, target_lon)
        self.radius_miles = radius_miles
        self.geocoder = Nominatim(user_agent="construction_lead_generator")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to coordinates.

        Args:
            address: Address string to geocode

        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding failed for '{address}': {e}")
            return None

    def calculate_distance(
        self,
        lat: float,
        lon: float,
        target_coords: Optional[Tuple[float, float]] = None
    ) -> float:
        """
        Calculate distance between two points in miles.

        Args:
            lat: Latitude of point
            lon: Longitude of point
            target_coords: Optional target coordinates (defaults to self.target_coords)

        Returns:
            Distance in miles
        """
        if target_coords is None:
            target_coords = self.target_coords

        point1 = (lat, lon)
        distance = geodesic(target_coords, point1).miles
        return round(distance, 2)

    def is_within_radius(
        self,
        lat: float,
        lon: float,
        radius_miles: Optional[float] = None
    ) -> bool:
        """
        Check if coordinates are within target radius.

        Args:
            lat: Latitude to check
            lon: Longitude to check
            radius_miles: Optional radius override (defaults to self.radius_miles)

        Returns:
            True if within radius, False otherwise
        """
        if radius_miles is None:
            radius_miles = self.radius_miles

        distance = self.calculate_distance(lat, lon)
        return distance <= radius_miles

    def get_distance_from_address(self, address: str) -> Optional[float]:
        """
        Get distance from target for a given address.

        Args:
            address: Address to check

        Returns:
            Distance in miles or None if geocoding fails
        """
        coords = self.geocode_address(address)
        if coords:
            return self.calculate_distance(coords[0], coords[1])
        return None

    def is_address_in_radius(self, address: str) -> bool:
        """
        Check if an address is within the target radius.

        Args:
            address: Address to check

        Returns:
            True if within radius, False otherwise
        """
        distance = self.get_distance_from_address(address)
        if distance is None:
            return False
        return distance <= self.radius_miles

    def get_cities_in_radius(self) -> list[str]:
        """
        Get a list of major cities within the target radius.

        Returns:
            List of city names within radius
        """
        # Major cities/areas near Omaha, NE (within ~35 miles)
        nearby_cities = [
            "Omaha, NE",
            "Bellevue, NE",
            "Papillion, NE",
            "La Vista, NE",
            "Council Bluffs, IA",
            "Elkhorn, NE",
            "Gretna, NE",
            "Ralston, NE",
            "Boys Town, NE",
            "Carter Lake, IA",
            "Chalco, NE",
            "Bennington, NE",
            "Waterloo, NE",
            "Valley, NE",
            "Springfield, NE",
            "Ashland, NE",
            "Plattsmouth, NE",
            "Underwood, IA",
            "Treynor, IA",
        ]
        return nearby_cities

    def get_search_area_description(self) -> str:
        """
        Get a description of the search area for search queries.

        Returns:
            Search area description string
        """
        cities = self.get_cities_in_radius()
        return f"Omaha, Nebraska metropolitan area (including {', '.join(cities[:5])})"

    @staticmethod
    def parse_address_components(address: str) -> dict:
        """
        Parse address string into components.

        Args:
            address: Full address string

        Returns:
            Dictionary with address components
        """
        # Basic address parsing (can be enhanced)
        parts = [p.strip() for p in address.split(',')]

        components = {
            'full_address': address,
            'street': None,
            'city': None,
            'state': None,
            'zip_code': None,
        }

        if len(parts) >= 1:
            components['street'] = parts[0]
        if len(parts) >= 2:
            components['city'] = parts[1]
        if len(parts) >= 3:
            # Try to extract state and zip from last part
            last_part = parts[2].strip()
            state_zip = last_part.split()
            if len(state_zip) >= 1:
                components['state'] = state_zip[0]
            if len(state_zip) >= 2:
                components['zip_code'] = state_zip[1]

        return components
