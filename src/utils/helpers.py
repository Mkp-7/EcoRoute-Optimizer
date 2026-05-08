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
    # State to major city mapping
    STATE_TO_CITY = {
        "california": "los angeles",
        "ca": "los angeles",
        "texas": "houston",
        "tx": "houston",
        "florida": "miami",
        "fl": "miami",
        "illinois": "chicago",
        "il": "chicago",
        "washington": "seattle",
        "wa": "seattle",
        "oregon": "portland",
        "or": "portland",
        "nevada": "las vegas",
        "nv": "las vegas",
        "arizona": "phoenix",
        "az": "phoenix",
        "colorado": "denver",
        "co": "denver",
        "georgia": "atlanta",
        "ga": "atlanta",
        "massachusetts": "boston",
        "ma": "boston",
        "pennsylvania": "philadelphia",
        "pa": "philadelphia",
        "ohio": "columbus",
        "michigan": "detroit",
        "mi": "detroit",
        "minnesota": "minneapolis",
        "mn": "minneapolis",
        "missouri": "st louis",
        "mo": "st louis",
        "tennessee": "nashville",
        "tn": "nashville",
        "north carolina": "charlotte",
        "nc": "charlotte",
        "south carolina": "charleston",
        "sc": "charleston",
        "louisiana": "new orleans",
        "la": "new orleans",  # Note: LA also means Los Angeles
        "alabama": "birmingham",
        "al": "birmingham",
        "kentucky": "louisville",
        "ky": "louisville",
        "oklahoma": "oklahoma city",
        "ok": "oklahoma city",
        "utah": "salt lake city",
        "ut": "salt lake city",
        "new mexico": "albuquerque",
        "nm": "albuquerque",
        "virginia": "richmond",
        "va": "richmond",
        "maryland": "baltimore",
        "md": "baltimore",
        "wisconsin": "milwaukee",
        "wi": "milwaukee",
        "indiana": "indianapolis",
        "in": "indianapolis",
        "connecticut": "hartford",
        "ct": "hartford",
        "iowa": "des moines",
        "ia": "des moines",
        "kansas": "kansas city",
        "ks": "kansas city",
        "arkansas": "little rock",
        "ar": "little rock",
        "mississippi": "jackson",
        "ms": "jackson",
        "nebraska": "omaha",
        "ne": "omaha",
        "rhode island": "providence",
        "ri": "providence",
        "new hampshire": "manchester",
        "nh": "manchester",
        "idaho": "boise",
        "id": "boise",
    }
    
    # City name aliases (abbreviations, nicknames, variants)
    CITY_ALIASES = {
        # New York
        "nyc": "new york",
        "ny": "new york",
        "new york city": "new york",
        
        # Los Angeles
        "la": "los angeles",
        "l.a.": "los angeles",
        "l a": "los angeles",
        
        # San Francisco
        "sf": "san francisco",
        "san fran": "san francisco",
        "frisco": "san francisco",
        "s.f.": "san francisco",
        
        # Chicago
        "chi": "chicago",
        "chi-town": "chicago",
        
        # Philadelphia
        "philly": "philadelphia",
        "phila": "philadelphia",
        
        # Washington
        "dc": "washington",
        "d.c.": "washington",
        "washington dc": "washington",
        "washington d.c.": "washington",
        
        # Miami
        "mia": "miami",
        
        # Boston
        "bos": "boston",
        
        # Seattle
        "sea": "seattle",
        
        # Las Vegas
        "vegas": "las vegas",
        "lv": "las vegas",
        
        # San Diego
        "sd": "san diego",
        
        # San Jose
        "sj": "san jose",
        
        # Phoenix
        "phx": "phoenix",
        
        # Dallas
        "dfw": "dallas",
        
        # Houston
        "hou": "houston",
        
        # Atlanta
        "atl": "atlanta",
        
        # Detroit
        "det": "detroit",
        
        # Minneapolis
        "minn": "minneapolis",
        "mpls": "minneapolis",
        
        # New Orleans
        "nola": "new orleans",
        "n.o.": "new orleans",
        
        # Indianapolis
        "indy": "indianapolis",
        
        # Portland
        "pdx": "portland",
        
        # Denver
        "den": "denver",
        
        # Charlotte
        "clt": "charlotte",
        
        # Nashville
        "nash": "nashville",
        
        # Austin
        "atx": "austin",
        
        # Jacksonville
        "jax": "jacksonville",
        
        # San Antonio
        "sa": "san antonio",
        "satx": "san antonio",
    }
    
    # Major US city coordinates (lon, lat)
    CITY_COORDS = {
        # California (14 cities)
        "san francisco": (-122.4194, 37.7749),
        "los angeles": (-118.2437, 34.0522),
        "san diego": (-117.1611, 32.7157),
        "sacramento": (-121.4944, 38.5816),
        "oakland": (-122.2712, 37.8044),
        "san jose": (-121.8863, 37.3382),
        "fresno": (-119.7871, 36.7378),
        "long beach": (-118.1937, 33.7701),
        "bakersfield": (-119.0187, 35.3733),
        "anaheim": (-117.9145, 33.8366),
        "riverside": (-117.3961, 33.9533),
        "stockton": (-121.2908, 37.9577),
        "irvine": (-117.8265, 33.6846),
        "santa ana": (-117.8678, 33.7455),
        
        # New York Metro (6 cities)
        "new york": (-74.0060, 40.7128),
        "manhattan": (-73.9712, 40.7831),
        "brooklyn": (-73.9442, 40.6782),
        "queens": (-73.7949, 40.7282),
        "bronx": (-73.8648, 40.8448),
        "staten island": (-74.1502, 40.5795),
        
        # New Jersey (7 cities)
        "newark": (-74.1724, 40.7357),
        "jersey city": (-74.0431, 40.7178),
        "paterson": (-74.1718, 40.9168),
        "elizabeth": (-74.2107, 40.6640),
        "clifton": (-74.1638, 40.8584),
        "passaic": (-74.1285, 40.8568),
        "hoboken": (-74.0320, 40.7439),
        
        # Texas (6 cities)
        "houston": (-95.3698, 29.7604),
        "dallas": (-96.7970, 32.7767),
        "austin": (-97.7431, 30.2672),
        "san antonio": (-98.4936, 29.4241),
        "fort worth": (-97.3308, 32.7555),
        "el paso": (-106.4850, 31.7619),
        
        # Florida (6 cities)
        "miami": (-80.1918, 25.7617),
        "orlando": (-81.3792, 28.5383),
        "tampa": (-82.4572, 27.9506),
        "jacksonville": (-81.6557, 30.3322),
        "fort lauderdale": (-80.1373, 26.1224),
        "st petersburg": (-82.6403, 27.7703),
        
        # Midwest (15 cities)
        "chicago": (-87.6298, 41.8781),
        "detroit": (-83.0458, 42.3314),
        "milwaukee": (-87.9065, 43.0389),
        "minneapolis": (-93.2650, 44.9778),
        "indianapolis": (-86.1581, 39.7684),
        "columbus": (-82.9988, 39.9612),
        "st louis": (-90.1994, 38.6270),
        "kansas city": (-94.5786, 39.0997),
        "memphis": (-90.0490, 35.1495),
        "cincinnati": (-84.5120, 39.1031),
        "cleveland": (-81.6944, 41.4993),
        "omaha": (-95.9345, 41.2565),
        "des moines": (-93.6091, 41.5868),
        "wichita": (-97.3301, 37.6872),
        "toledo": (-83.5379, 41.6528),
        
        # Northeast (10 cities)
        "boston": (-71.0589, 42.3601),
        "philadelphia": (-75.1652, 39.9526),
        "baltimore": (-76.6122, 39.2904),
        "washington": (-77.0369, 38.9072),
        "pittsburgh": (-79.9959, 40.4406),
        "providence": (-71.4128, 41.8240),
        "hartford": (-72.6859, 41.7658),
        "buffalo": (-78.8784, 42.8864),
        "rochester": (-77.6088, 43.1566),
        "syracuse": (-76.1474, 43.0481),
        
        # Southeast (10 cities)
        "atlanta": (-84.3880, 33.7490),
        "charlotte": (-80.8431, 35.2271),
        "nashville": (-86.7816, 36.1627),
        "raleigh": (-78.6382, 35.7796),
        "richmond": (-77.4360, 37.5407),
        "norfolk": (-76.2859, 36.8508),
        "greensboro": (-79.7920, 36.0726),
        "winston salem": (-80.2442, 36.0999),
        "louisville": (-85.7585, 38.2527),
        "charleston": (-79.9311, 32.7765),
        
        # Southwest (8 cities)
        "phoenix": (-112.0740, 33.4484),
        "las vegas": (-115.1398, 36.1699),
        "tucson": (-110.9747, 32.2226),
        "albuquerque": (-106.6504, 35.0844),
        "mesa": (-111.8315, 33.4152),
        "scottsdale": (-111.9261, 33.4942),
        "glendale": (-112.1860, 33.5387),
        "chandler": (-111.8413, 33.3062),
        
        # Northwest (6 cities)
        "seattle": (-122.3321, 47.6062),
        "portland": (-122.6765, 45.5152),
        "denver": (-104.9903, 39.7392),
        "salt lake city": (-111.8910, 40.7608),
        "spokane": (-117.4260, 47.6588),
        "boise": (-116.2146, 43.6150),
        
        # South (9 cities)
        "new orleans": (-90.0715, 29.9511),
        "birmingham": (-86.8025, 33.5207),
        "little rock": (-92.2896, 34.7465),
        "jackson": (-90.1848, 32.2988),
        "montgomery": (-86.3007, 32.3668),
        "mobile": (-88.0399, 30.6954),
        "shreveport": (-93.7502, 32.5252),
        "baton rouge": (-91.1871, 30.4515),
        "oklahoma city": (-97.5164, 35.4676),
        
        # Additional cities
        "manchester": (-71.5381, 42.9956),
    }
    
    city_lower = city_name.lower().strip()
    
    # Remove state suffix if present (e.g., "Seattle, WA" -> "Seattle")
    if ',' in city_lower:
        city_lower = city_lower.split(',')[0].strip()
    
    # Check if it's a state name FIRST (before aliases)
    # Special handling for "LA" - prefer Los Angeles over Louisiana
    if city_lower == "la":
        city_lower = "los angeles"
    elif city_lower in STATE_TO_CITY:
        city_lower = STATE_TO_CITY[city_lower]
    
    # Check city aliases
    if city_lower in CITY_ALIASES:
        city_lower = CITY_ALIASES[city_lower]
    
    # Direct match
    if city_lower in CITY_COORDS:
        return CITY_COORDS[city_lower]
    
    # Try to find partial match
    for city_key, coords in CITY_COORDS.items():
        if city_key in city_lower or city_lower in city_key:
            return coords
    
    return None


def get_grid_zone_for_city(city_name: str) -> str:
    """Get electricity grid zone for a city"""
    city_lower = city_name.lower().strip()
    return CITY_GRID_MAPPING.get(city_lower, "US-MISO")


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
    Estimate road distance (adds 20% to straight-line distance)
    """
    straight_line = haversine_distance(coord1, coord2)
    return straight_line * 1.20


def calculate_distance(origin: str, destination: str) -> Optional[float]:
    """
    Calculate distance between two cities
    
    Args:
        origin: Origin city name
        destination: Destination city name
    
    Returns:
        Distance in kilometers or None if cities not found
    """
    origin_coords = geocode_city(origin)
    destination_coords = geocode_city(destination)
    
    if not origin_coords or not destination_coords:
        return None
    
    return estimate_road_distance(origin_coords, destination_coords)


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


def format_time(hours: float) -> str:
    """Format time in hours and days"""
    days = hours / 24
    if days >= 1:
        return f"{hours:.1f} hours ({days:.1f} days)"
    return f"{hours:.1f} hours"


def calculate_trees_equivalent(kg_co2: float) -> float:
    """
    Calculate number of trees needed to offset carbon
    One tree absorbs ~21 kg CO2 per year
    """
    return kg_co2 / 21.0


def calculate_cars_equivalent(kg_co2: float) -> float:
    """
    Calculate equivalent to taking cars off road for a day
    Average car emits ~4.6 kg CO2 per day
    """
    return kg_co2 / 4.6


if __name__ == "__main__":
    # Test functions
    print("🧪 Testing Helper Functions\n")
    
    # Test geocoding
    sf = geocode_city("san francisco")
    print(f"San Francisco coordinates: {sf}")
    
    la = geocode_city("los angeles")
    print(f"Los Angeles coordinates: {la}")
    
    # Test state mapping
    ca = geocode_city("california")
    print(f"California (→ LA) coordinates: {ca}")
    
    tx = geocode_city("texas")
    print(f"Texas (→ Houston) coordinates: {tx}")
    
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
