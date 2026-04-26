"""
Helper utilities for EcoRoute Optimizer
"""

from typing import Tuple, Optional
from math import radians, cos, sin, asin, sqrt, atan2, degrees
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import CITY_GRID_MAPPING


def geocode_city(city_name: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for major US cities
    
    Args:
        city_name: City name (case-insensitive)
    
    Returns:
        (longitude, latitude) tuple or None
    """
    # Major US city coordinates (lon, lat)
    CITY_COORDS = {
        # Major cities
        "san francisco": (-122.4194, 37.7749),
        "los angeles": (-118.2437, 34.0522),
        "san diego": (-117.1611, 32.7157),
        "sacramento": (-121.4944, 38.5816),
        "new york": (-74.0060, 40.7128),
        "chicago": (-87.6298, 41.8781),
        "houston": (-95.3698, 29.7604),
        "dallas": (-96.7970, 32.7767),
        "austin": (-97.7431, 30.2672),
        "boston": (-71.0589, 42.3601),
        "atlanta": (-84.3880, 33.7490),
        "seattle": (-122.3321, 47.6062),
        "portland": (-122.6765, 45.5152),
        "denver": (-104.9903, 39.7392),
        "phoenix": (-112.0740, 33.4484),
        "las vegas": (-115.1398, 36.1699),
        "miami": (-80.1918, 25.7617),
        "philadelphia": (-75.1652, 39.9526),
        "washington": (-77.0369, 38.9072),
        "kansas city": (-94.5786, 39.0997),
        "memphis": (-90.0490, 35.1495),
        "oakland": (-122.2712, 37.8044),
        "modesto": (-120.9969, 37.6391),
        "jacksonville": (-81.6557, 30.3322),
        
        # NYC Boroughs
        "manhattan": (-73.9712, 40.7831),
        "brooklyn": (-73.9442, 40.6782),
        "queens": (-73.7949, 40.7282),
        "bronx": (-73.8648, 40.8448),
        "staten island": (-74.1502, 40.5795),
        
        # New Jersey
        "newark": (-74.1724, 40.7357),
        "jersey city": (-74.0431, 40.7178),
        "paterson": (-74.1718, 40.9168),
        "elizabeth": (-74.2107, 40.6640),
        "clifton": (-74.1638, 40.8584),
        "passaic": (-74.1285, 40.8568),
        "hoboken": (-74.0320, 40.7439),
        
        # More major cities
        "detroit": (-83.0458, 42.3314),
        "charlotte": (-80.8431, 35.2271),
        "columbus": (-82.9988, 39.9612),
        "indianapolis": (-86.1581, 39.7684),
        "baltimore": (-76.6122, 39.2904),
        "nashville": (-86.7816, 36.1627),
        "milwaukee": (-87.9065, 43.0389),
        "minneapolis": (-93.2650, 44.9778),
        "pittsburgh": (-79.9959, 40.4406),
        "cincinnati": (-84.5120, 39.1031),
        "cleveland": (-81.6944, 41.4993),
        "tampa": (-82.4572, 27.9506),
        "orlando": (-81.3792, 28.5383),
        "st louis": (-90.1994, 38.6270),
        "raleigh": (-78.6382, 35.7796),
    }
    
    city_lower = city_name.lower().strip()
    
    # Direct match
    if city_lower in CITY_COORDS:
        return CITY_COORDS[city_lower]
    
    # Try to extract city name if formatted like "City, State"
    if ',' in city_lower:
        city_part = city_lower.split(',')[0].strip()
        if city_part in CITY_COORDS:
            return CITY_COORDS[city_part]
    
    # Try to find partial match
    for city_key, coords in CITY_COORDS.items():
        if city_key in city_lower or city_lower in city_key:
            return coords
    
    return None


def get_grid_zone_for_city(city_name: str) -> str:
    """Get electricity grid zone for a city"""
    city_lower = city_name.lower().strip()
    return CITY_GRID_MAPPING.get(city_lower, "US-MISO")  # Default to Midwest


def haversine_distance(coord1: Tuple[float, float], 
                      coord2: Tuple[float, float]) -> float:
    """
    Calculate great-circle distance between two points
    
    Args:
        coord1: (longitude, latitude)
        coord2: (longitude, latitude)
    
    Returns:
        Distance in kilometers
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Earth radius in km
    km = 6371 * c
    
    return km


def estimate_road_distance(coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
    """
    Estimate road distance (adds 15% to straight-line distance)
    """
    straight_line = haversine_distance(coord1, coord2)
    return straight_line * 1.15


def lbs_to_kg(pounds: float) -> float:
    """Convert pounds to kilograms"""
    return pounds * 0.453592


def kg_to_lbs(kilograms: float) -> float:
    """Convert kilograms to pounds"""
    return kilograms * 2.20462


def mi_to_km(miles: float) -> float:
    """Convert miles to kilometers"""
    return miles * 1.60934


def km_to_mi(kilometers: float) -> float:
    """Convert kilometers to miles"""
    return kilometers * 0.621371


def calculate_bearing(coord1: Tuple[float, float], 
                     coord2: Tuple[float, float]) -> float:
    """
    Calculate initial bearing between two coordinates
    
    Returns:
        Bearing in degrees (0-360)
    """
    lon1, lat1 = map(radians, coord1)
    lon2, lat2 = map(radians, coord2)
    
    dlon = lon2 - lon1
    
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    
    initial_bearing = atan2(x, y)
    
    # Convert to degrees
    bearing = (degrees(initial_bearing) + 360) % 360
    
    return bearing


def format_currency(amount: float) -> str:
    """Format currency with $ sign and 2 decimals"""
    return f"${amount:,.2f}"


def format_distance(km: float, unit: str = "km") -> str:
    """Format distance with unit"""
    if unit == "mi":
        mi = km_to_mi(km)
        return f"{mi:,.1f} mi"
    return f"{km:,.1f} km"


def format_carbon(kg_co2: float) -> str:
    """Format carbon emissions"""
    if kg_co2 >= 1000:
        tons = kg_co2 / 1000
        return f"{tons:.2f} tons CO2"
    return f"{kg_co2:.1f} kg CO2"


def calculate_trees_equivalent(kg_co2: float) -> float:
    """
    Calculate number of trees needed to offset carbon
    One tree absorbs ~20 kg CO2 per year
    """
    return kg_co2 / 20


def calculate_cars_equivalent(kg_co2: float) -> float:
    """
    Calculate equivalent to taking cars off road for a day
    Average car emits ~4.6 kg CO2 per day
    """
    return kg_co2 / 4.6


# Import atan2 and degrees for bearing calculation
from math import atan2, degrees


if __name__ == "__main__":
    # Test functions
    print("🧪 Testing Helper Functions\n")
    
    # Test geocoding
    sf = geocode_city("san francisco")
    print(f"San Francisco coordinates: {sf}")
    
    la = geocode_city("los angeles")
    print(f"Los Angeles coordinates: {la}")
    
    # Test distance
    if sf and la:
        distance = haversine_distance(sf, la)
        print(f"\nSF to LA straight-line: {distance:.1f} km")
        
        road_distance = estimate_road_distance(sf, la)
        print(f"SF to LA road estimate: {road_distance:.1f} km")
    
    # Test conversions
    print(f"\n500 lbs = {lbs_to_kg(500):.1f} kg")
    print(f"100 km = {km_to_mi(100):.1f} mi")
    
    # Test formatting
    print(f"\n{format_currency(1234.56)}")
    print(f"{format_distance(500)}")
    print(f"{format_carbon(145.8)}")
    
    # Test equivalents
    print(f"\n145 kg CO2 = {calculate_trees_equivalent(145):.1f} trees")
    print(f"145 kg CO2 = {calculate_cars_equivalent(145):.1f} cars off road/day")
