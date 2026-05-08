"""
Utility helper functions for EcoRoute Optimizer
"""

import math
from typing import Optional, Tuple


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate great circle distance between two points on Earth
    using the Haversine formula
    
    Args:
        coord1: (longitude, latitude) tuple for first point
        coord2: (longitude, latitude) tuple for second point
    
    Returns:
        Distance in kilometers
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def estimate_road_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Estimate road distance from straight-line distance
    Adds ~20% to account for roads not being straight
    
    Args:
        coord1: (longitude, latitude) tuple for first point
        coord2: (longitude, latitude) tuple for second point
    
    Returns:
        Estimated road distance in kilometers
    """
    straight_line = haversine_distance(coord1, coord2)
    # Roads are typically 20% longer than straight line
    return straight_line * 1.2


def geocode_city(city_name: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for major US cities
    
    Args:
        city_name: City name (case-insensitive)
    
    Returns:
        (longitude, latitude) tuple or None
    """
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
        
        # Boston
        "bos": "boston",
        
        # Miami
        "mia": "miami",
        
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
        
        # New York Metro (12 cities)
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
        "hoboken": (-74.0323, 40.7439),
        
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
        "chandler": (
