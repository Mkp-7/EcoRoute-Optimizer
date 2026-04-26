"""
API Clients for EcoRoute Optimizer
Wrappers for external APIs with caching and rate limiting
"""

import requests
import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import (
    ELECTRICITY_MAP_API_KEY,
    CARBON_INTERFACE_API_KEY,
    OPENROUTE_SERVICE_API_KEY,
    OPENWEATHER_API_KEY,
    API_ENDPOINTS,
)
from src.data.database import db


class ElectricityMapClient:
    """Client for Electricity Map API - Carbon Intensity Data"""
    
    def __init__(self):
        self.api_key = ELECTRICITY_MAP_API_KEY
        self.base_url = "https://api.electricitymaps.com/v3"
        self.cache_hours = 1  # Cache for 1 hour
    
    def get_carbon_intensity(self, zone: str) -> Optional[Dict]:
        """
        Get current carbon intensity for a grid zone
        
        Args:
            zone: Grid zone code (e.g., 'US-CAL-CISO')
        
        Returns:
            Dict with carbon intensity data or None if error
        """
        # Check cache first
        cached = db.get_cached_carbon_intensity(zone, max_age_hours=self.cache_hours)
        if cached is not None:
            print(f"✓ Using cached carbon intensity for {zone}: {cached} gCO2/kWh")
            return {"carbonIntensity": cached, "zone": zone, "cached": True}
        
        # Make API call
        try:
            url = f"{self.base_url}/carbon-intensity/latest"
            params = {"zone": zone}
            headers = {"auth-token": self.api_key}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                carbon_intensity = data.get("carbonIntensity", 0)
                
                # Cache the result
                db.cache_carbon_intensity(zone, zone, carbon_intensity)
                
                print(f"✓ Fetched carbon intensity for {zone}: {carbon_intensity} gCO2/kWh")
                return data
            
            elif response.status_code == 401:
                print(f"⚠️  Electricity Map API: Unauthorized (check API key)")
                return None
            
            elif response.status_code == 404:
                print(f"⚠️  Zone {zone} not found. Using default estimate.")
                # Return US average as fallback
                default_intensity = 385  # US grid average
                return {"carbonIntensity": default_intensity, "zone": zone, "estimated": True}
            
            else:
                print(f"⚠️  Electricity Map API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Error fetching carbon intensity: {e}")
            # Return fallback value
            return {"carbonIntensity": 385, "zone": zone, "error": str(e)}
    
    def get_average_intensity_along_route(self, zones: list) -> float:
        """Get average carbon intensity across multiple zones"""
        intensities = []
        
        for zone in zones:
            data = self.get_carbon_intensity(zone)
            if data:
                intensities.append(data.get("carbonIntensity", 385))
        
        if intensities:
            avg = sum(intensities) / len(intensities)
            print(f"✓ Average carbon intensity across route: {avg:.1f} gCO2/kWh")
            return avg
        
        return 385  # US average fallback


class OpenRouteServiceClient:
    """Client for OpenRouteService API - Routing and Distances"""
    
    def __init__(self):
        self.api_key = OPENROUTE_SERVICE_API_KEY
        self.base_url = "https://api.openrouteservice.org/v2"
    
    def get_route(self, origin: Tuple[float, float], 
                  destination: Tuple[float, float],
                  profile: str = "driving-hgv") -> Optional[Dict]:
        """
        Get route between two coordinates
        
        Args:
            origin: (longitude, latitude) tuple
            destination: (longitude, latitude) tuple
            profile: 'driving-hgv' (heavy truck) or 'driving-car'
        
        Returns:
            Dict with distance (km) and duration (hours)
        """
        try:
            url = f"{self.base_url}/directions/{profile}"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "coordinates": [list(origin), list(destination)],
                "units": "km"
            }
            
            response = requests.post(url, json=body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                route = data["routes"][0]
                summary = route["summary"]
                
                distance_km = summary["distance"]  # Already in km
                duration_hours = summary["duration"] / 3600  # Convert seconds to hours
                
                print(f"✓ Route calculated: {distance_km:.1f} km, {duration_hours:.1f} hours")
                
                return {
                    "distance_km": distance_km,
                    "duration_hours": duration_hours,
                    "geometry": route.get("geometry")
                }
            
            elif response.status_code == 401:
                print(f"⚠️  OpenRoute API: Unauthorized (check API key)")
                return None
            
            else:
                print(f"⚠️  OpenRoute API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Error calculating route: {e}")
            return None
    
    def get_distance_estimate(self, origin_coords: Tuple[float, float],
                             dest_coords: Tuple[float, float]) -> float:
        """
        Get straight-line distance estimate (fallback)
        Uses Haversine formula
        """
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1 = origin_coords
        lon2, lat2 = dest_coords
        
        # Convert to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c  # Earth radius in km
        
        # Add 15% for road distance vs straight line
        road_km = km * 1.15
        
        print(f"✓ Estimated distance: {road_km:.1f} km (straight-line + 15%)")
        return road_km


class OpenWeatherClient:
    """Client for OpenWeatherMap API - Weather Data"""
    
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache_hours = 6  # Weather changes slowly
    
    def get_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather for coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with weather data
        """
        # Check cache first
        location_key = f"{lat:.2f},{lon:.2f}"
        cached = db.get_cached_weather(location_key, max_age_hours=self.cache_hours)
        
        if cached:
            print(f"✓ Using cached weather for {location_key}")
            return cached
        
        # Make API call
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_data = {
                    "temperature_c": data["main"]["temp"],
                    "wind_speed_kmh": data["wind"]["speed"] * 3.6,  # m/s to km/h
                    "wind_direction_deg": data["wind"].get("deg", 0),
                    "conditions": data["weather"][0]["description"],
                }
                
                # Cache the result
                db.cache_weather(location_key, weather_data)
                
                print(f"✓ Weather: {weather_data['temperature_c']:.1f}°C, "
                      f"Wind: {weather_data['wind_speed_kmh']:.1f} km/h")
                
                return weather_data
            
            elif response.status_code == 401:
                print(f"⚠️  OpenWeather API: Unauthorized (check API key)")
                return None
            
            else:
                print(f"⚠️  OpenWeather API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Error fetching weather: {e}")
            return None
    
    def get_wind_impact(self, wind_speed_kmh: float, 
                       wind_direction: float,
                       travel_direction: float) -> float:
        """
        Calculate fuel efficiency impact from wind
        
        Args:
            wind_speed_kmh: Wind speed in km/h
            wind_direction: Wind direction in degrees (0-360)
            travel_direction: Travel direction in degrees (0-360)
        
        Returns:
            Impact factor (e.g., 0.10 = 10% more fuel, -0.05 = 5% less fuel)
        """
        # Calculate relative angle (headwind vs tailwind)
        angle_diff = abs(wind_direction - travel_direction)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Headwind (0-45 degrees) increases fuel use
        # Tailwind (135-180 degrees) decreases fuel use
        # Crosswind (45-135 degrees) minimal impact
        
        if angle_diff < 45:  # Headwind
            if wind_speed_kmh > 30:
                impact = 0.15  # Strong headwind: +15% fuel
            elif wind_speed_kmh > 15:
                impact = 0.08  # Moderate headwind: +8% fuel
            else:
                impact = 0.03  # Light headwind: +3% fuel
        
        elif angle_diff > 135:  # Tailwind
            if wind_speed_kmh > 30:
                impact = -0.10  # Strong tailwind: -10% fuel
            elif wind_speed_kmh > 15:
                impact = -0.05  # Moderate tailwind: -5% fuel
            else:
                impact = -0.02  # Light tailwind: -2% fuel
        
        else:  # Crosswind
            impact = 0.0  # Minimal impact
        
        return impact


class CarbonInterfaceClient:
    """Client for Carbon Interface API - Emissions Calculation"""
    
    def __init__(self):
        self.api_key = CARBON_INTERFACE_API_KEY
        self.base_url = "https://www.carboninterface.com/api/v1"
    
    def estimate_shipping_emissions(self, weight_kg: float, 
                                    distance_km: float,
                                    transport_method: str = "truck") -> Optional[Dict]:
        """
        Estimate carbon emissions for shipping
        
        Args:
            weight_kg: Shipment weight in kg
            distance_km: Distance in km
            transport_method: 'truck', 'rail', 'ship', 'plane'
        
        Returns:
            Dict with carbon estimate in kg CO2
        """
        try:
            url = f"{self.base_url}/estimates"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Convert to pounds and miles for API
            weight_lb = weight_kg * 2.20462
            distance_mi = distance_km * 0.621371
            
            body = {
                "type": "shipping",
                "weight_value": weight_lb,
                "weight_unit": "lb",
                "distance_value": distance_mi,
                "distance_unit": "mi",
                "transport_method": transport_method
            }
            
            response = requests.post(url, json=body, headers=headers, timeout=15)
            
            if response.status_code == 201:
                data = response.json()
                carbon_kg = data["data"]["attributes"]["carbon_kg"]
                
                print(f"✓ Carbon Interface estimate: {carbon_kg:.2f} kg CO2")
                
                return {
                    "carbon_kg": carbon_kg,
                    "weight_kg": weight_kg,
                    "distance_km": distance_km,
                    "method": transport_method
                }
            
            elif response.status_code == 401:
                print(f"⚠️  Carbon Interface API: Unauthorized (check API key)")
                return None
            
            else:
                print(f"⚠️  Carbon Interface API error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ Error estimating emissions: {e}")
            return None


# Initialize clients
electricity_map = ElectricityMapClient()
openroute = OpenRouteServiceClient()
openweather = OpenWeatherClient()
carbon_interface = CarbonInterfaceClient()


# Test function
def test_api_clients():
    """Test all API clients"""
    print("\n🧪 Testing API Clients...\n")
    
    # Test 1: Carbon Intensity
    print("1️⃣  Testing Electricity Map API...")
    intensity = electricity_map.get_carbon_intensity("US-CAL-CISO")
    print(f"   Result: {intensity}\n")
    
    # Test 2: Routing
    print("2️⃣  Testing OpenRouteService API...")
    # San Francisco to Los Angeles
    sf_coords = (-122.4194, 37.7749)
    la_coords = (-118.2437, 34.0522)
    route = openroute.get_route(sf_coords, la_coords)
    print(f"   Result: {route}\n")
    
    # Test 3: Weather
    print("3️⃣  Testing OpenWeather API...")
    weather = openweather.get_weather(37.7749, -122.4194)
    print(f"   Result: {weather}\n")
    
    # Test 4: Carbon Interface
    print("4️⃣  Testing Carbon Interface API...")
    emissions = carbon_interface.estimate_shipping_emissions(
        weight_kg=500,
        distance_km=600,
        transport_method="truck"
    )
    print(f"   Result: {emissions}\n")
    
    print("✅ All API tests complete!\n")


if __name__ == "__main__":
    test_api_clients()
