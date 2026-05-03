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
    
    # Optional API keys (not required, but some files may import them)
    ELECTRICITY_MAP_API_KEY = st.secrets.get("ELECTRICITY_MAP_API_KEY", "")
    CARBON_INTERFACE_API_KEY = st.secrets.get("CARBON_INTERFACE_API_KEY", "")
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")
    
except:
    # Running locally - use .env
    from dotenv import load_dotenv
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    OPENROUTE_SERVICE_API_KEY = os.getenv("OPENROUTE_SERVICE_API_KEY", "")
    
    # Optional API keys
    ELECTRICITY_MAP_API_KEY = os.getenv("ELECTRICITY_MAP_API_KEY", "")
    CARBON_INTERFACE_API_KEY = os.getenv("CARBON_INTERFACE_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Database path
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "ecoroute.db"
PROJECT_ROOT = BASE_DIR

# Debug settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

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

# Dictionary formats (some files use these)
AVERAGE_SPEEDS = {
    "diesel_truck": 80,
    "electric_truck": 75,
    "rail": 65,
    "intermodal": 55,
}

COST_PER_KM = {
    "diesel_truck": 1.20,
    "electric_truck": 1.15,
    "rail": 0.45,
    "intermodal": 0.85,
}

EMISSIONS_FACTORS = {
    "diesel_truck": 0.62,
    "electric_truck": 0.18,
    "rail": 0.08,
    "intermodal": 0.15,
}

# Legacy single-value constants (backward compatibility)
SPEED_KMH = DIESEL_SPEED_KMH
EMISSIONS_KG_PER_KM = DIESEL_EMISSIONS_KG_PER_KM

# Weather impact factors
WEATHER_IMPACT = {
    "headwind_strong": 0.15,
    "headwind_moderate": 0.08,
    "tailwind_moderate": -0.05,
    "tailwind_strong": -0.10,
}

# API endpoints
API_ENDPOINTS = {
    "electricity_map": "https://api.electricitymap.org/v3/carbon-intensity/latest",
    "carbon_interface": "https://www.carboninterface.com/api/v1/estimates",
    "openroute": "https://api.openrouteservice.org/v2/directions/driving-car",
    "openweather": "https://api.openweathermap.org/data/2.5/weather",
}

# API Rate Limits
ELECTRICITY_MAP_RATE_LIMIT = int(os.getenv("ELECTRICITY_MAP_RATE_LIMIT", "50"))
CARBON_INTERFACE_RATE_LIMIT = int(os.getenv("CARBON_INTERFACE_RATE_LIMIT", "200"))
OPENROUTE_RATE_LIMIT = int(os.getenv("OPENROUTE_RATE_LIMIT", "2000"))
OPENWEATHER_RATE_LIMIT = int(os.getenv("OPENWEATHER_RATE_LIMIT", "1000"))

# Carbon pricing
CARBON_OFFSET_PRICE_PER_TON = float(os.getenv("CARBON_OFFSET_PRICE_PER_TON", "15.00"))

# Grid carbon intensity (kg CO2 per kWh) - EPA eGRID 2023
GRID_CARBON_INTENSITY = {
    "US-CAL-CISO": 200,
    "US-MISO": 450,
    "US-NY": 250,
    "US-NY-NYIS": 250,
    "US-PJM": 380,
    "US-SPP": 500,
    "US-ERCOT": 400,
    "US-TEX-ERCO": 400,
    "US-WECC": 350,
    "US-NW-PACW": 100,
    "US-SE-SOCO": 420,
    "US-SW-AZPS": 380,
    "US-NEISO": 270,
    "US-AVERAGE": 385
}

# Grid zones
GRID_ZONES = {
    "california": "US-CAL-CISO",
    "texas": "US-TEX-ERCO",
    "new_york": "US-NY-NYIS",
    "new_england": "US-NEISO",
    "midwest": "US-MISO",
    "pjm": "US-PJM",
    "southeast": "US-SE-SOCO",
    "southwest": "US-SW-AZPS",
    "northwest": "US-NW-PACW",
}

# City to grid zone mapping
CITY_GRID_MAPPING = {
    # California
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
    "new york": "US-NY-NYIS",
    "manhattan": "US-NY-NYIS",
    "brooklyn": "US-NY-NYIS",
    "queens": "US-NY-NYIS",
    "bronx": "US-NY-NYIS",
    "staten island": "US-NY-NYIS",
    
    # New Jersey
    "newark": "US-PJM",
    "jersey city": "US-PJM",
    "paterson": "US-PJM",
    "elizabeth": "US-PJM",
    "clifton": "US-PJM",
    "passaic": "US-PJM",
    "hoboken": "US-PJM",
    
    # Midwest
    "chicago": "US-MISO",
    "detroit": "US-MISO",
    "milwaukee": "US-MISO",
    "minneapolis": "US-MISO",
    "indianapolis": "US-MISO",
    "columbus": "US-MISO",
    "st louis": "US-MISO",
    "memphis": "US-MISO",
    
    # Texas
    "houston": "US-TEX-ERCO",
    "dallas": "US-TEX-ERCO",
    "austin": "US-TEX-ERCO",
    
    # Other cities
    "seattle": "US-NW-PACW",
    "portland": "US-NW-PACW",
    "denver": "US-NW-PACW",
    "phoenix": "US-SW-AZPS",
    "las vegas": "US-NW-PACW",
    "miami": "US-SE-SOCO",
    "atlanta": "US-SE-SOCO",
    "boston": "US-NEISO",
    "philadelphia": "US-PJM",
    "baltimore": "US-PJM",
    "washington": "US-PJM",
    "charlotte": "US-SE-SOCO",
    "nashville": "US-SE-SOCO",
    "kansas city": "US-SPP",
    "pittsburgh": "US-PJM",
    "cincinnati": "US-PJM",
    "cleveland": "US-PJM",
    "tampa": "US-SE-SOCO",
    "orlando": "US-SE-SOCO",
    "jacksonville": "US-SE-SOCO",
    "raleigh": "US-SE-SOCO",
}

# Rail hubs for intermodal routing
RAIL_HUBS = [
    "chicago",
    "kansas city",
    "memphis",
    "dallas",
    "los angeles",
    "oakland",
    "seattle",
    "atlanta",
    "jacksonville",
    "newark",
    "philadelphia",
]
