"""
Configuration settings for GreenRoute AI
Loads environment variables and provides centralized config access
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELECTRICITY_MAP_API_KEY = os.getenv("ELECTRICITY_MAP_API_KEY", "")
CARBON_INTERFACE_API_KEY = os.getenv("CARBON_INTERFACE_API_KEY", "")
OPENROUTE_SERVICE_API_KEY = os.getenv("OPENROUTE_SERVICE_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATABASE_PATH = PROJECT_ROOT / os.getenv("DATABASE_PATH", "data/ecoroute.db")

# API Rate Limits (requests per day)
ELECTRICITY_MAP_RATE_LIMIT = int(os.getenv("ELECTRICITY_MAP_RATE_LIMIT", "50"))
CARBON_INTERFACE_RATE_LIMIT = int(os.getenv("CARBON_INTERFACE_RATE_LIMIT", "200"))
OPENROUTE_RATE_LIMIT = int(os.getenv("OPENROUTE_RATE_LIMIT", "2000"))
OPENWEATHER_RATE_LIMIT = int(os.getenv("OPENWEATHER_RATE_LIMIT", "1000"))

# Carbon Pricing
CARBON_OFFSET_PRICE_PER_TON = float(os.getenv("CARBON_OFFSET_PRICE_PER_TON", "15.00"))

# Vehicle Emissions Factors (kg CO2 per km)
EMISSIONS_FACTORS = {
    "diesel_truck": float(os.getenv("DIESEL_TRUCK_EMISSIONS", "0.62")),
    "electric_truck": float(os.getenv("ELECTRIC_TRUCK_EMISSIONS", "0.18")),
    "rail": float(os.getenv("RAIL_EMISSIONS", "0.08")),
    "intermodal": 0.15,  # Weighted average of truck + rail
}

# Fuel Efficiency Adjustments (percentage impact)
WEATHER_IMPACT = {
    "headwind_strong": 0.15,  # 15% more fuel
    "headwind_moderate": 0.08,
    "tailwind_moderate": -0.05,  # 5% less fuel
    "tailwind_strong": -0.10,
}

# Cost per km by vehicle type (USD)
COST_PER_KM = {
    "diesel_truck": 1.20,
    "electric_truck": 1.15,
    "rail": 0.45,
    "intermodal": 0.85,
}

# Average speeds (km/h)
AVERAGE_SPEEDS = {
    "diesel_truck": 80,
    "electric_truck": 75,  # Slightly slower due to charging stops
    "rail": 65,
    "intermodal": 55,  # Slower due to transfers
}

# API Endpoints
API_ENDPOINTS = {
    "electricity_map": "https://api.electricitymap.org/v3/carbon-intensity/latest",
    "carbon_interface": "https://www.carboninterface.com/api/v1/estimates",
    "openroute": "https://api.openrouteservice.org/v2/directions/driving-car",
    "openweather": "https://api.openweathermap.org/data/2.5/weather",
}

# US Electricity Grid Zones (for Electricity Map API)
GRID_ZONES = {
    "california": "US-CAL-CISO",
    "texas": "US-TEX-ERCO",
    "new_york": "US-NY-NYIS",
    "new_england": "US-NEISO",
    "midwest": "US-MISO",
    "pjm": "US-PJM",  # Mid-Atlantic
    "southeast": "US-SE-SOCO",
    "southwest": "US-SW-AZPS",
    "northwest": "US-NW-PACW",
}

# Major US Cities and their grid zones
CITY_GRID_MAPPING = {
    "san francisco": "US-CAL-CISO",
    "los angeles": "US-CAL-CISO",
    "san diego": "US-CAL-CISO",
    "sacramento": "US-CAL-CISO",
    "oakland": "US-CAL-CISO",
    "new york": "US-NY-NYIS",
    "manhattan": "US-NY-NYIS",
    "brooklyn": "US-NY-NYIS",
    "queens": "US-NY-NYIS",
    "bronx": "US-NY-NYIS",
    "staten island": "US-NY-NYIS",
    "chicago": "US-MISO",
    "houston": "US-TEX-ERCO",
    "dallas": "US-TEX-ERCO",
    "austin": "US-TEX-ERCO",
    "boston": "US-NEISO",
    "atlanta": "US-SE-SOCO",
    "seattle": "US-NW-PACW",
    "portland": "US-NW-PACW",
    "denver": "US-NW-PACW",
    "phoenix": "US-SW-AZPS",
    "las vegas": "US-NW-PACW",
    "miami": "US-SE-SOCO",
    "philadelphia": "US-PJM",
    "washington": "US-PJM",
    "baltimore": "US-PJM",
    "newark": "US-PJM",
    "jersey city": "US-PJM",
    "paterson": "US-PJM",
    "elizabeth": "US-PJM",
    "clifton": "US-PJM",
    "passaic": "US-PJM",
    "hoboken": "US-PJM",
    "detroit": "US-MISO",
    "charlotte": "US-SE-SOCO",
    "columbus": "US-PJM",
    "indianapolis": "US-MISO",
    "nashville": "US-SE-SOCO",
    "milwaukee": "US-MISO",
    "minneapolis": "US-MISO",
    "pittsburgh": "US-PJM",
    "cincinnati": "US-PJM",
    "cleveland": "US-PJM",
    "tampa": "US-SE-SOCO",
    "orlando": "US-SE-SOCO",
    "st louis": "US-MISO",
    "raleigh": "US-SE-SOCO",
}

# Rail Hub Cities (for intermodal routing)
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
    "newark",  # NYC area rail hub
    "philadelphia",  # Northeast corridor
]

# Validation
def validate_config():
    """Validate that required API keys are set"""
    required_keys = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    }
    
    missing = [key for key, value in required_keys.items() if not value]
    
    if missing:
        print(f"⚠️  Warning: Missing required API keys: {', '.join(missing)}")
        print("Some features may not work. Please set them in your .env file.")
        return False
    
    return True

# Optional: Check config on import
if __name__ != "__main__":
    validate_config()
