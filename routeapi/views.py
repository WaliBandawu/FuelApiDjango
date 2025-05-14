import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status   
from .services.geocoding import GeocodingService
from .services.routing import RoutingService
from .serializers import RouteRequestSerializer
from django.shortcuts import render

logger = logging.getLogger(__name__)



class OptimizeRouteView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_addr = serializer.validated_data['start']
        dest_addr = serializer.validated_data['destination']
        start_time = time.time()

        # Geocode both addresses
        start_coords = GeocodingService.geocode_address(start_addr)
        dest_coords = GeocodingService.geocode_address(dest_addr)
        if not start_coords or not dest_coords:
            return Response({"error": "Invalid start or destination address."}, status=400)

        # Retrieve route between coordinates
        route = RoutingService.get_route(start_coords, dest_coords)
        if not route:
            return Response({"error": "Unable to retrieve route."}, status=400)

        geometry = route['features'][0]['geometry']
        if geometry['type'] != 'LineString' or 'coordinates' not in geometry:
            return Response({"error": "Invalid geometry format from ORS."}, status=400)

        # Extract lat/lon points and compute distance
        coords = [[coord[1], coord[0]] for coord in geometry['coordinates']]
        distance_miles = route['features'][0]['properties']['segments'][0]['distance'] / 1609.34
        fuel_needed = distance_miles / RoutingService.MPG

        # Calculate refuel points and best stations
        refuel_points = RoutingService.get_refueling_points(coords)
        optimal_stops = RoutingService.find_cheapest_stations(refuel_points)
        total_cost = sum(stop['gallons'] * stop['price'] for stop in optimal_stops)

        processing_time = time.time() - start_time

        return Response({
            "start": start_addr,
            "destination": dest_addr,
            "distance_miles": round(distance_miles, 2),
            "fuel_needed_gallons": round(fuel_needed, 2),
            "total_fuel_cost_usd": round(total_cost, 2),
            "optimal_stops": optimal_stops,
            "route_geometry": geometry,
            "processing_time_sec": round(processing_time, 2)
        }, status=200)

def route_map_view(request):
    return render(request, 'route_optimizer_map.html')