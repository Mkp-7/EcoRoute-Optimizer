"""
Configuration settings for EcoRoute Optimizer
"""
import os
from pathlib import Path

# Try Streamlit secrets first, then fall back to .env
try:
    import streamlit as st
    # Running on Streamlit Cloud - use secrets
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
    OPENROUTE_SERVICE_API_KEY = st.secrets.get("OPENROUTE_SERVICE_API_KEY", "")
except:
    # Running locally - use .env
    from dotenv import load_dotenv
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    OPENROUTE_SERVICE_API_KEY = os.getenv("OPENROUTE_SERVICE_API_KEY", "")

# Database path
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "ecoroute.db"

# EPA emissions factors (kg CO2 per km)
DIESEL_EMISSIONS_KG_PER_KM = 0.62
ELECTRIC_EMISSIONS_KG_PER_KM = 0.08
RAIL_EMISSIONS_KG_PER_KM = 0.15

# Cost factors ($ per km)
DIESEL_COST_PER_KM = 1.20
ELECTRIC_COST_PER_KM = 0.60
RAIL_COST_PER_KM = 0.85

# Average speeds (km/h)
DIESEL_SPEED_KMH = 80
ELECTRIC_SPEED_KMH = 75
RAIL_SPEED_KMH = 55

# Grid carbon intensity (kg CO2 per kWh) - EPA eGRID 2023
GRID_CARBON_INTENSITY = {
    "US-CAL-CISO": 200,      # California
    "US-MISO": 450,          # Midwest
    "US-NY": 250,            # New York
    "US-PJM": 380,           # Mid-Atlantic
    "US-SPP": 500,           # Central
    "US-ERCOT": 400,         # Texas
    "US-WECC": 350,          # Western
    "US-AVERAGE": 385        # National average
}

# City to grid zone mapping
CITY_GRID_MAPPING = {
    # California (all use CISO grid)
    "san francisco": "US-CAL-CISO",
    "los angeles": "US-CAL-CISO",
    "san diego": "US-CAL-CISO",
    "sacramento": "US-CAL-CISO",
    "oakland": "US-CAL-CISO",
    "san jose": "US-CAL-CISO",
    "fresno": "US-CAL-CISO",
    "long beach": "US-CAL-CISO",
    "bakersfield": "US-CAL-CISO",
    "anaheim": "US-CAL-CISO",
    "riverside": "US-CAL-CISO",
    "stockton": "US-CAL-CISO",
    "irvine": "US-CAL-CISO",
    "santa ana": "US-CAL-CISO",
    
    # New York
    "new york": "US-NY",
    "manhattan": "US-NY",
    "brooklyn": "US-NY",
    "queens": "US-NY",
    "bronx": "US-NY",
    "staten island": "US-NY",
    
    # New Jersey (PJM)
    "newark": "US-PJM",
    "jersey city": "US-PJM",
    "paterson": "US-PJM",
    "elizabeth": "US-PJM",
    "clifton": "US-PJM",
    "passaic": "US-PJM",
    "hoboken": "US-PJM",
    
    # Midwest (MISO)
    "chicago": "US-MISO",
    "detroit": "US-MISO",
    "milwaukee": "US-MISO",
    "minneapolis": "US-MISO",
    "indianapolis": "US-MISO",
    "columbus": "US-MISO",
    "st louis": "US-MISO",
    "memphis": "US-MISO",
    
    # Texas (ERCOT)
    "houston": "US-ERCOT",
    "dallas": "US-ERCOT",
    "austin": "US-ERCOT",
    
    # Other major cities
    "seattle": "US-WECC",
    "portland": "US-WECC",
    "denver": "US-WECC",
    "phoenix": "US-WECC",
    "las vegas": "US-WECC",
    "miami": "US-PJM",
    "atlanta": "US-PJM",
    "boston": "US-PJM",
    "philadelphia": "US-PJM",
    "baltimore": "US-PJM",
    "washington": "US-PJM",
    "charlotte": "US-PJM",
    "nashville": "US-MISO",
    "kansas city": "US-SPP",
    "pittsburgh": "US-PJM",
    "cincinnati": "US-PJM",
    "cleveland": "US-PJM",
    "tampa": "US-PJM",
    "orlando": "US-PJM",
    "jacksonville": "US-PJM",
    "raleigh": "US-PJM",
}
