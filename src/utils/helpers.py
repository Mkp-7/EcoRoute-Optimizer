def geocode_city(city_name: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for major US cities
    
    Args:
        city_name: City name (case-insensitive)
    
    Returns:
        (longitude, latitude) tuple or None
    """
    # State abbreviations mapping
    STATE_ALIASES = {
        # Full state names to abbreviations
        "california": "CA",
        "new york": "NY",
        "texas": "TX",
        "florida": "FL",
        "illinois": "IL",
        "pennsylvania": "PA",
        "ohio": "OH",
        "georgia": "GA",
        "north carolina": "NC",
        "michigan": "MI",
        "new jersey": "NJ",
        "virginia": "VA",
        "washington": "WA",
        "arizona": "AZ",
        "massachusetts": "MA",
        "tennessee": "TN",
        "indiana": "IN",
        "missouri": "MO",
        "maryland": "MD",
        "wisconsin": "WI",
        "colorado": "CO",
        "minnesota": "MN",
        "south carolina": "SC",
        "alabama": "AL",
        "louisiana": "LA",
        "kentucky": "KY",
        "oregon": "OR",
        "oklahoma": "OK",
        "connecticut": "CT",
        "utah": "UT",
        "iowa": "IA",
        "nevada": "NV",
        "arkansas": "AR",
        "mississippi": "MS",
        "kansas": "KS",
        "new mexico": "NM",
        "nebraska": "NE",
        "west virginia": "WV",
        "idaho": "ID",
        "hawaii": "HI",
        "new hampshire": "NH",
        "maine": "ME",
        "montana": "MT",
        "rhode island": "RI",
        "delaware": "DE",
        "south dakota": "SD",
        "north dakota": "ND",
        "alaska": "AK",
        "vermont": "VT",
        "wyoming": "WY",
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
        "chandler": (-111.8413, 33.3062),
        
        # Northwest (6 cities)
        "seattle": (-122.3321, 47.6062),
        "portland": (-122.6750, 45.5152),
        "denver": (-104.9903, 39.7392),
        "salt lake city": (-111.8910, 40.7608),
        "spokane": (-117.4260, 47.6588),
        "boise": (-116.2146, 43.6150),
        
        # South (8 cities)
        "new orleans": (-90.0715, 29.9511),
        "birmingham": (-86.8025, 33.5207),
        "little rock": (-92.2896, 34.7465),
        "jackson": (-90.1848, 32.2988),
        "montgomery": (-86.3007, 32.3668),
        "mobile": (-88.0399, 30.6954),
        "shreveport": (-93.7502, 32.5252),
        "baton rouge": (-91.1871, 30.4515),
    }
    
    city_lower = city_name.lower().strip()
    
    # Remove state suffixes if present (e.g., "Seattle, WA" -> "Seattle")
    if ',' in city_lower:
        city_part = city_lower.split(',')[0].strip()
    else:
        city_part = city_lower
    
    # Check aliases first
    if city_part in CITY_ALIASES:
        city_part = CITY_ALIASES[city_part]
    
    # Direct match
    if city_part in CITY_COORDS:
        return CITY_COORDS[city_part]
    
    # If not found, return None
    return None
