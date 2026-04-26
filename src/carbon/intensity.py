"""
Carbon Intensity Data - Static Regional Averages
No API required - uses EPA and EIA published data
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import CITY_GRID_MAPPING

# US Grid Carbon Intensity by Region (gCO2/kWh)
# Source: EPA eGRID 2023 data + EIA
REGIONAL_CARBON_INTENSITY = {
    # California - Clean grid (lots of solar, wind, hydro)
    "US-CAL-CISO": 200,
    
    # Texas - Medium (mix of gas, wind, some coal)
    "US-TEX-ERCO": 400,
    
    # New York - Clean (nuclear, hydro, gas)
    "US-NY-NYIS": 250,
    
    # New England - Clean (nuclear, hydro, gas)
    "US-NEISO": 280,
    
    # Midwest - Higher (coal, gas, some wind)
    "US-MISO": 450,
    
    # Mid-Atlantic (PJM) - Medium-high (coal, nuclear, gas)
    "US-PJM": 380,
    
    # Southeast - Medium-high (coal, nuclear, gas)
    "US-SE-SOCO": 420,
    
    # Southwest - Medium (gas, solar)
    "US-SW-AZPS": 350,
    
    # Northwest - Very clean (hydro, wind)
    "US-NW-PACW": 150,
}

# US National Average
US_AVERAGE_CARBON_INTENSITY = 385  # gCO2/kWh


def get_carbon_intensity(zone: str) -> float:
    """
    Get carbon intensity for a grid zone
    
    Args:
        zone: Grid zone code (e.g., 'US-CAL-CISO')
    
    Returns:
        Carbon intensity in gCO2/kWh
    """
    return REGIONAL_CARBON_INTENSITY.get(zone, US_AVERAGE_CARBON_INTENSITY)


def get_carbon_intensity_for_city(city_name: str) -> float:
    """
    Get carbon intensity for a city
    
    Args:
        city_name: City name (e.g., 'san francisco')
    
    Returns:
        Carbon intensity in gCO2/kWh
    """
    city_lower = city_name.lower().strip()
    grid_zone = CITY_GRID_MAPPING.get(city_lower, "US-MISO")
    return get_carbon_intensity(grid_zone)


def get_average_intensity_along_route(origin_city: str, dest_city: str) -> float:
    """
    Get average carbon intensity along a route
    
    Args:
        origin_city: Origin city name
        dest_city: Destination city name
    
    Returns:
        Average carbon intensity in gCO2/kWh
    """
    origin_intensity = get_carbon_intensity_for_city(origin_city)
    dest_intensity = get_carbon_intensity_for_city(dest_city)
    
    # Simple average (could be weighted by distance in each grid in future)
    avg_intensity = (origin_intensity + dest_intensity) / 2
    
    return avg_intensity


def get_grid_cleanliness_label(intensity: float) -> str:
    """
    Get human-readable label for grid cleanliness
    
    Args:
        intensity: Carbon intensity in gCO2/kWh
    
    Returns:
        Label: 'Very Clean', 'Clean', 'Medium', 'High Carbon'
    """
    if intensity < 200:
        return "Very Clean (lots of renewables)"
    elif intensity < 300:
        return "Clean (low carbon mix)"
    elif intensity < 400:
        return "Medium (mixed sources)"
    else:
        return "High Carbon (fossil fuel heavy)"


def compare_to_national_average(intensity: float) -> dict:
    """
    Compare grid intensity to US national average
    
    Args:
        intensity: Carbon intensity in gCO2/kWh
    
    Returns:
        Dict with comparison metrics
    """
    diff = intensity - US_AVERAGE_CARBON_INTENSITY
    pct_diff = (diff / US_AVERAGE_CARBON_INTENSITY) * 100
    
    if diff < 0:
        comparison = f"{abs(pct_diff):.0f}% cleaner than US average"
    elif diff > 0:
        comparison = f"{pct_diff:.0f}% dirtier than US average"
    else:
        comparison = "Same as US average"
    
    return {
        "intensity": intensity,
        "us_average": US_AVERAGE_CARBON_INTENSITY,
        "difference": diff,
        "percent_difference": pct_diff,
        "comparison": comparison,
        "cleanliness": get_grid_cleanliness_label(intensity),
    }


# Test function
def test_carbon_intensity():
    """Test carbon intensity functions"""
    print("\n🔌 Testing Carbon Intensity Data\n")
    
    # Test 1: By city
    print("1️⃣  Carbon Intensity by City:")
    cities = ["san francisco", "new york", "chicago", "houston", "seattle"]
    for city in cities:
        intensity = get_carbon_intensity_for_city(city)
        label = get_grid_cleanliness_label(intensity)
        print(f"   {city.title():15s}: {intensity:3.0f} gCO2/kWh - {label}")
    
    print("\n2️⃣  Route Average:")
    origin, dest = "san francisco", "chicago"
    avg = get_average_intensity_along_route(origin, dest)
    print(f"   {origin.title()} → {dest.title()}: {avg:.0f} gCO2/kWh (average)")
    
    print("\n3️⃣  Comparison to US Average:")
    for city in ["san francisco", "seattle", "chicago"]:
        intensity = get_carbon_intensity_for_city(city)
        comparison = compare_to_national_average(intensity)
        print(f"   {city.title():15s}: {comparison['comparison']}")
    
    print("\n✅ Carbon intensity data ready!\n")


if __name__ == "__main__":
    test_carbon_intensity()
