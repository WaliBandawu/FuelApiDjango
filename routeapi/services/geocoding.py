"""Module for handling geocoding services and related functionality."""

# Standard library imports
import hashlib
import logging
import os
import time

# Third-party imports
from functools import lru_cache
import requests
from django.core.cache import cache


from routeapi.services.loader import load_fuel_data

logger = logging.getLogger(__name__)

# Preload fuel dataset once at module import
fuel_df = load_fuel_data('fuel_prices_with_coords.csv')

# Add a normalized key for geocoding lookup
fuel_df['address_key'] = (
    fuel_df['City'].str.lower().str.strip() + ', ' + fuel_df['State'].str.lower().str.strip()
)

class GeocodingService:
    """Service class for handling geocoding operations using Nominatim and OpenCage APIs."""
    NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
    OPENCAGE_URL = 'https://api.opencagedata.com/geocode/v1/json'
    OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')

    @staticmethod
    @lru_cache(maxsize=128)
    def geocode_address(address: str) -> dict:
        """
        Geocode the given address and return its coordinates.

        Args:
            address (str): The address to geocode

        Returns:
            dict: Dictionary containing geocoding results with coordinates
        """
        normalized_address = address.strip().lower()
        cache_key = f"geocode_{hashlib.md5(normalized_address.encode()).hexdigest()}"
        

        # 1. Check Django cache
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 2. Check in local dataset
        match = fuel_df[fuel_df['address_key'] == normalized_address]
        if not match.empty:
            result = {
                'lat': float(match.iloc[0]['lat']),
                'lon': float(match.iloc[0]['lon'])
            }
            cache.set(cache_key, result, 86400)
            return result

        # 3. Try Nominatim API
        try:
            time.sleep(1)  # Respect rate limits
            response = requests.get(
                GeocodingService.NOMINATIM_URL,
                params={
                    'q': address,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'us'
                },
                headers={'User-Agent': 'YourAppName (your@email.com)'},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            if data:
                result = {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
                cache.set(cache_key, result, 86400)
                return result
        except requests.RequestException as e:
            logger.warning("Nominatim error for '%s': %s", address, e)

        # 4. Try OpenCage API
        try:
            response = requests.get(
                GeocodingService.OPENCAGE_URL,
                params={
                    'q': address,
                    'key': GeocodingService.OPENCAGE_API_KEY,
                    'limit': 1,
                    'countrycode': 'us'
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            if data.get('results'):
                geom = data['results'][0]['geometry']
                result = {'lat': geom['lat'], 'lon': geom['lng']}
                cache.set(cache_key, result, 86400)
                return result
        except requests.RequestException as e:
            logger.error("OpenCage error for '%s': %s", address, e)
        

        return None
