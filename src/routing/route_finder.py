"""
Route Finder for EcoRoute Optimizer
Generates route options: diesel truck, electric truck, rail, intermodal
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import (
    COST_PER_KM,
    AVERAGE_SPEEDS,
    RAIL_HUBS,
)
from src.utils.helpers import (
    geocode_city,
    haversine_distance,
    estimate_road_distance,
)
from src.utils.api_clients import openroute, openweather
from src.carbon.calculator import calculator
from src.carbon.intensity import get_average_intensity_along_route


class RouteFinder:
    """Find and generate route options between cities"""
    
    def __init__(self):
        self.cost_per_km = COST_PER_KM
        self.speeds = AVERAGE_SPEEDS
        self.rail_hubs = [hub.lower() for hub in RAIL_HUBS]
    
    def get_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a city"""
        coords = geocode_city(city_name)
        if not coords:
            print(f"⚠️  City not found: {city_name}")
        return coords
    
    def calculate_distance(self, origin: str, destination: str) -> Optional[float]:
        """
        Calculate route distance in km
        
        Args:
            origin: Origin city name
            destination: Destination city name
        
        Returns:
            Distance in km, or None if cities not found
        """
        # Get coordinates
        origin_coords = self.get_coordinates(origin)
        dest_coords = self.get_coordinates(destination)
        
        if not origin_coords or not dest_coords:
            return None
        
        # Try OpenRouteService API first
        try:
            route_data = openroute.get_route(origin_coords, dest_coords)
            if route_data:
                distance = route_data['distance_km']
                print(f"✓ API distance {origin} → {destination}: {distance:.1f} km")
                return distance
        except Exception as e:
            print(f"⚠️  API failed, using estimate: {e}")
        
        # Fallback to Haversine + 15% for road distance
        distance = estimate_road_distance(origin_coords, dest_coords)
        print(f"✓ Estimated distance {origin} → {destination}: {distance:.1f} km")
        return distance
    
    def calculate_route_cost(self, distance_km: float, vehicle_type: str) -> float:
        """Calculate route cost in USD"""
        cost_per_km = self.cost_per_km.get(vehicle_type, 1.0)
        return distance_km * cost_per_km
    
    def calculate_route_time(self, distance_km: float, vehicle_type: str) -> float:
        """Calculate route time in hours"""
        avg_speed = self.speeds.get(vehicle_type, 75)
        return distance_km / avg_speed
    
    def find_direct_truck_route(self, origin: str, destination: str,
                               weight_lbs: float = 1000,
                               vehicle_type: str = "diesel_truck") -> Optional[Dict]:
        """
        Find direct truck route (diesel or electric)
        
        Args:
            origin: Origin city
            destination: Destination city
            weight_lbs: Shipment weight
            vehicle_type: 'diesel_truck' or 'electric_truck'
        
        Returns:
            Route dict with distance, cost, time, carbon
        """
        distance = self.calculate_distance(origin, destination)
        if not distance:
            return None
        
        # Calculate cost
        cost = self.calculate_route_cost(distance, vehicle_type)
        
        # Calculate time
        time_hours = self.calculate_route_time(distance, vehicle_type)
        
        # Get weather for fuel adjustment
        origin_coords = self.get_coordinates(origin)
        weather_impact = 0.0
        
        if origin_coords:
            try:
                weather = openweather.get_weather(origin_coords[1], origin_coords[0])
                if weather:
                    # Simplified: assume moderate wind impact
                    wind_speed = weather.get('wind_speed_kmh', 0)
                    if wind_speed > 20:
                        weather_impact = 0.08  # +8% fuel for moderate wind
            except:
                pass
        
        # Get grid carbon intensity for route (for EVs)
        grid_intensity = None
        if vehicle_type == "electric_truck":
            grid_intensity = get_average_intensity_along_route(origin, destination)
        
        # Calculate carbon emissions
        emissions_result = calculator.calculate_total_emissions(
            distance_km=distance,
            vehicle_type=vehicle_type,
            weight_lbs=weight_lbs,
            weather_impact=weather_impact,
            grid_intensity=grid_intensity
        )
        
        carbon_kg = emissions_result['final_emissions_kg']
        
        return {
            "mode": "direct_truck",
            "vehicle_type": vehicle_type,
            "origin": origin,
            "destination": destination,
            "distance_km": round(distance, 1),
            "cost_usd": round(cost, 2),
            "time_hours": round(time_hours, 1),
            "carbon_kg": carbon_kg,
            "weather_impact": weather_impact,
            "grid_intensity": grid_intensity,
            "route_description": f"Direct {vehicle_type.replace('_', ' ')} from {origin} to {destination}"
        }
    
    def find_nearest_rail_hub(self, city: str) -> Optional[str]:
        """Find nearest rail hub to a city"""
        city_coords = self.get_coordinates(city)
        if not city_coords:
            return None
        
        min_distance = float('inf')
        nearest_hub = None
        
        for hub in self.rail_hubs:
            hub_coords = self.get_coordinates(hub)
            if hub_coords:
                dist = haversine_distance(city_coords, hub_coords)
                if dist < min_distance:
                    min_distance = dist
                    nearest_hub = hub
        
        return nearest_hub
    
    def find_intermodal_route(self, origin: str, destination: str,
                             weight_lbs: float = 1000) -> Optional[Dict]:
        """
        Find intermodal route: truck → rail → truck
        
        Args:
            origin: Origin city
            destination: Destination city
            weight_lbs: Shipment weight
        
        Returns:
            Route dict with total distance, cost, time, carbon
        """
        # Find nearest rail hubs
        origin_hub = self.find_nearest_rail_hub(origin)
        dest_hub = self.find_nearest_rail_hub(destination)
        
        if not origin_hub or not dest_hub:
            print(f"⚠️  No rail hubs found for intermodal routing")
            return None
        
        # If origin/destination ARE rail hubs, use them directly
        if origin.lower() in self.rail_hubs:
            origin_hub = origin
        if destination.lower() in self.rail_hubs:
            dest_hub = destination
        
        # Calculate three legs
        # Leg 1: Origin → Origin Hub (truck)
        leg1_distance = self.calculate_distance(origin, origin_hub) if origin.lower() != origin_hub.lower() else 0
        
        # Leg 2: Origin Hub → Dest Hub (rail)
        leg2_distance = self.calculate_distance(origin_hub, dest_hub)
        
        # Leg 3: Dest Hub → Destination (truck)
        leg3_distance = self.calculate_distance(dest_hub, destination) if destination.lower() != dest_hub.lower() else 0
        
        if not leg2_distance:
            return None
        
        total_distance = (leg1_distance or 0) + leg2_distance + (leg3_distance or 0)
        
        # Calculate costs (weighted by mode)
        truck_distance = (leg1_distance or 0) + (leg3_distance or 0)
        rail_distance = leg2_distance
        
        truck_cost = truck_distance * self.cost_per_km['diesel_truck']
        rail_cost = rail_distance * self.cost_per_km['rail']
        total_cost = truck_cost + rail_cost
        
        # Calculate time (includes transfer time)
        truck_time = truck_distance / self.speeds['diesel_truck']
        rail_time = rail_distance / self.speeds['rail']
        transfer_time = 4  # 4 hours for rail transfers
        total_time = truck_time + rail_time + transfer_time
        
        # Calculate carbon (weighted by mode)
        truck_carbon = calculator.calculate_total_emissions(
            distance_km=truck_distance,
            vehicle_type='diesel_truck',
            weight_lbs=weight_lbs
        )['final_emissions_kg'] if truck_distance > 0 else 0
        
        rail_carbon = calculator.calculate_total_emissions(
            distance_km=rail_distance,
            vehicle_type='rail',
            weight_lbs=weight_lbs
        )['final_emissions_kg']
        
        total_carbon = truck_carbon + rail_carbon
        
        return {
            "mode": "intermodal",
            "vehicle_type": "truck_rail_truck",
            "origin": origin,
            "destination": destination,
            "origin_hub": origin_hub,
            "dest_hub": dest_hub,
            "distance_km": round(total_distance, 1),
            "cost_usd": round(total_cost, 2),
            "time_hours": round(total_time, 1),
            "carbon_kg": round(total_carbon, 2),
            "legs": {
                "truck_to_hub_km": round(leg1_distance or 0, 1),
                "rail_km": round(leg2_distance, 1),
                "hub_to_dest_km": round(leg3_distance or 0, 1),
            },
            "route_description": f"Truck from {origin} to {origin_hub}, rail to {dest_hub}, truck to {destination}"
        }
    
    def generate_all_routes(self, origin: str, destination: str,
                           weight_lbs: float = 1000,
                           deadline_hours: Optional[float] = None) -> List[Dict]:
        """
        Generate all viable route options
        
        Args:
            origin: Origin city
            destination: Destination city
            weight_lbs: Shipment weight in pounds
            deadline_hours: Optional delivery deadline
        
        Returns:
            List of route dicts sorted by carbon emissions
        """
        routes = []
        
        print(f"\nGenerating routes: {origin} to {destination}")
        print(f"   Weight: {weight_lbs} lbs")
        if deadline_hours:
            print(f"   Deadline: {deadline_hours} hours")
        print()
        
        # 1. Diesel truck (baseline)
        print("1. Finding diesel truck route...")
        diesel_route = self.find_direct_truck_route(origin, destination, weight_lbs, "diesel_truck")
        if diesel_route:
            routes.append(diesel_route)
            print(f"   Done: {diesel_route['distance_km']} km, ${diesel_route['cost_usd']}, {diesel_route['carbon_kg']} kg CO2\n")
        
        # 2. Electric truck (if distance < 400 km)
        distance = self.calculate_distance(origin, destination)
        if distance and distance < 400:
            print("2. Finding electric truck route...")
            ev_route = self.find_direct_truck_route(origin, destination, weight_lbs, "electric_truck")
            if ev_route:
                routes.append(ev_route)
                print(f"   Done: {ev_route['distance_km']} km, ${ev_route['cost_usd']}, {ev_route['carbon_kg']} kg CO2\n")
        else:
            print("2. Electric truck not viable (distance > 400 km)\n")
        
        # 3. Intermodal (truck + rail)
        print("3. Finding intermodal route...")
        intermodal_route = self.find_intermodal_route(origin, destination, weight_lbs)
        if intermodal_route:
            routes.append(intermodal_route)
            print(f"   Done: {intermodal_route['distance_km']} km, ${intermodal_route['cost_usd']}, {intermodal_route['carbon_kg']} kg CO2\n")
        
        # Filter by deadline if specified
        if deadline_hours:
            routes = [r for r in routes if r['time_hours'] <= deadline_hours]
            print(f"Filtered to {len(routes)} routes meeting {deadline_hours}hr deadline\n")
        
        # Sort by carbon emissions (lowest first)
        routes.sort(key=lambda r: r['carbon_kg'])
        
        return routes


# Singleton instance
route_finder = RouteFinder()


# Convenience function
def find_routes(origin: str, destination: str, **kwargs) -> List[Dict]:
    """Quick route finding"""
    return route_finder.generate_all_routes(origin, destination, **kwargs)


# Test function
def test_route_finder():
    """Test route finder with sample routes"""
    print("\nTESTING ROUTE FINDER\n")
    print("=" * 70)
    
    # Test 1: San Francisco to Los Angeles (short route)
    print("\nTEST 1: San Francisco to Los Angeles (short route)")
    print("-" * 70)
    routes = find_routes("san francisco", "los angeles", weight_lbs=1000)
    
    if routes:
        print(f"\nFound {len(routes)} routes:\n")
        for i, route in enumerate(routes, 1):
            print(f"{i}. {route['vehicle_type'].upper()}")
            print(f"   Distance: {route['distance_km']} km")
            print(f"   Cost: ${route['cost_usd']}")
            print(f"   Time: {route['time_hours']} hours")
            print(f"   Carbon: {route['carbon_kg']} kg CO2")
            if i < len(routes):
                savings = routes[0]['carbon_kg'] - route['carbon_kg']
                pct = (savings / routes[0]['carbon_kg']) * 100
                print(f"   Savings vs diesel: {abs(savings):.1f} kg CO2 ({abs(pct):.1f}%)")
            print()
    
    # Test 2: San Francisco to Chicago (long route - intermodal opportunity)
    print("\nTEST 2: San Francisco to Chicago (long route)")
    print("-" * 70)
    routes = find_routes("san francisco", "chicago", weight_lbs=1500, deadline_hours=60)
    
    if routes:
        print(f"\nFound {len(routes)} routes meeting deadline:\n")
        for i, route in enumerate(routes, 1):
            print(f"{i}. {route['vehicle_type'].upper()}")
            print(f"   Distance: {route['distance_km']} km")
            print(f"   Cost: ${route['cost_usd']}")
            print(f"   Time: {route['time_hours']} hours")
            print(f"   Carbon: {route['carbon_kg']} kg CO2")
            
            if route['mode'] == 'intermodal':
                print(f"   Route: {route['route_description']}")
                print(f"   Legs: {route['legs']}")
            
            if i > 1:
                baseline = routes[0]['carbon_kg']
                savings = baseline - route['carbon_kg']
                pct = (savings / baseline) * 100
                print(f"   Carbon savings: {savings:.1f} kg CO2 ({pct:.1f}%)")
            print()
    
    print("=" * 70)
    print("ROUTE FINDER TESTS COMPLETE!\n")


if __name__ == "__main__":
    test_route_finder()
