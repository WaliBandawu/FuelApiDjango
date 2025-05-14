"""Module for handling routing operations and distance calculations between geographical points."""

import os
import logging
from geopy.distance import geodesic
import numpy as np
import openrouteservice
from django.core.cache import cache
from routeapi.services.loader import load_fuel_data

logger = logging.getLogger(__name__)

ORS_API_KEY = os.getenv('ORS_API_KEY')
ors_client = openrouteservice.Client(key=ORS_API_KEY)
MAX_RANGE_MILES = 500
STATION_SEARCH_RADIUS = 10  # miles
MPG = 10

FUEL_DATA = load_fuel_data('fuel_prices_with_coords.csv')


class RoutingService:
    MPG = MPG
    MAX_RANGE = MAX_RANGE_MILES
    SEARCH_RADIUS = STATION_SEARCH_RADIUS
    fuel_data = FUEL_DATA

    @staticmethod
    def get_route(start: dict, end: dict) -> dict:
        cache_key = f"route_{start['lat']}_{start['lon']}_{end['lat']}_{end['lon']}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            route = ors_client.directions(
                coordinates=[[start['lon'], start['lat']], [end['lon'], end['lat']]],
                profile='driving-car',
                format='geojson'
            )
            if 'features' in route and route['features']:
                cache.set(cache_key, route, 86400)  # Cache for 1 day
                return route
        except Exception as e:
            logger.error("Routing error: %s", e)
        return None

    @staticmethod
    def get_refueling_points(coords: list) -> list:
        """Calculate refueling points along a route based on given coordinates.

        Args:
            coords (list): List of coordinate pairs representing the route.

        Returns:
            list: List of recommended refueling points along the route.
        """
        points = []
        total_miles = 0.0
        points = []
        total_miles = 0.0
        last = coords[0]
        i = 10

        while i < len(coords):
            curr = coords[i]
            seg_dist = geodesic((last[0], last[1]), (curr[0], curr[1])).miles
            total_miles += seg_dist

            # When nearing range limit, find a nearby refueling segment
            if total_miles >= RoutingService.MAX_RANGE * 0.8:
                found = False
                for j in range(i, min(i + 20, len(coords))):
                    next_pt = coords[j]
                    dist = geodesic((last[0], last[1]), (next_pt[0], next_pt[1])).miles
                    if dist >= RoutingService.MAX_RANGE * 0.9:
                        continue
                    points.append({'lat': next_pt[0], 'lon': next_pt[1]})
                    total_miles = 0.0
                    last = next_pt
                    i = j + 1
                    found = True
                    break
                if not found:
                    break  # no more room to refuel, end route
            else:
                last = curr
                i += 10

        return points


    @staticmethod
    def find_cheapest_stations(refuel_points: list) -> list:
        """Find the cheapest fuel stations near each refueling point.

        Args:
            refuel_points (list): List of geographical points where refueling is needed.

        Returns:
            list: List of cheapest fuel stations near each refueling point.
        """
        if RoutingService.fuel_data.empty:
            return []
        if RoutingService.fuel_data.empty:
            return []

        results = []
        for point in refuel_points:
            lat_bin_range = [np.floor(point['lat'] * 2 - 0.5) / 2, np.floor(point['lat'] * 2 + 0.5) / 2]
            lon_bin_range = [np.floor(point['lon'] * 2 - 0.5) / 2, np.floor(point['lon'] * 2 + 0.5) / 2]

            candidates = RoutingService.fuel_data[
                (RoutingService.fuel_data['lat_bin'] >= lat_bin_range[0]) &
                (RoutingService.fuel_data['lat_bin'] <= lat_bin_range[1]) &
                (RoutingService.fuel_data['lon_bin'] >= lon_bin_range[0]) &
                (RoutingService.fuel_data['lon_bin'] <= lon_bin_range[1])
            ]

            if not candidates.empty:
                candidates = candidates.copy()
                candidates['distance'] = candidates.apply(
                    lambda row: geodesic((point['lat'], point['lon']), (row['lat'], row['lon'])).miles,
                    axis=1
                )
                nearby = candidates[candidates['distance'] <= RoutingService.SEARCH_RADIUS].sort_values('Retail Price')
                if not nearby.empty:
                    best = nearby.iloc[0]
                    gallons = RoutingService.MAX_RANGE / RoutingService.MPG
                    results.append({
                        'station_name': best['Truckstop Name'],
                        'station_address': f"{best['Address']}, {best['City']}, {best['State']}",
                        'station_lat': float(best['lat']),
                        'station_lon': float(best['lon']),
                        'price': float(best['Retail Price']),
                        'gallons': round(gallons, 2)
                    })

        return results
