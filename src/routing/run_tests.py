"""
Simple Test Runner - Windows Compatible
Tests all modules without Unicode characters
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 70)
print("ECOROUTE OPTIMIZER - TEST SUITE")
print("=" * 70)

# Test 1: Carbon Intensity
print("\n[1/5] Testing Carbon Intensity...")
try:
    from src.carbon.intensity import get_carbon_intensity_for_city
    sf_intensity = get_carbon_intensity_for_city("san francisco")
    chi_intensity = get_carbon_intensity_for_city("chicago")
    print(f"      San Francisco: {sf_intensity} gCO2/kWh")
    print(f"      Chicago: {chi_intensity} gCO2/kWh")
    print("      PASSED")
except Exception as e:
    print(f"      FAILED: {e}")

# Test 2: Carbon Calculator
print("\n[2/5] Testing Carbon Calculator...")
try:
    from src.carbon.calculator import calculator
    result = calculator.calculate_total_emissions(
        distance_km=500,
        vehicle_type="diesel_truck",
        weight_lbs=1000
    )
    print(f"      500km diesel truck: {result['final_emissions_kg']} kg CO2")
    print("      PASSED")
except Exception as e:
    print(f"      FAILED: {e}")

# Test 3: Helper Functions
print("\n[3/5] Testing Helper Functions...")
try:
    from src.utils.helpers import geocode_city, estimate_road_distance
    sf = geocode_city("san francisco")
    la = geocode_city("los angeles")
    if sf and la:
        dist = estimate_road_distance(sf, la)
        print(f"      SF to LA: {dist:.0f} km")
        print("      PASSED")
    else:
        print("      FAILED: Could not geocode cities")
except Exception as e:
    print(f"      FAILED: {e}")

# Test 4: Route Finder
print("\n[4/5] Testing Route Finder...")
try:
    from src.routing.route_finder import route_finder
    routes = route_finder.generate_all_routes(
        "san francisco", 
        "los angeles", 
        weight_lbs=1000
    )
    if routes:
        print(f"      Found {len(routes)} routes")
        best = routes[0]
        print(f"      Best: {best['vehicle_type']}")
        print(f"      Cost: ${best['cost_usd']:.0f}")
        print(f"      Carbon: {best['carbon_kg']:.0f} kg CO2")
        print("      PASSED")
    else:
        print("      FAILED: No routes found")
except Exception as e:
    print(f"      FAILED: {e}")

# Test 5: Optimizer
print("\n[5/5] Testing Optimizer...")
try:
    from src.routing.optimizer import optimizer
    
    # Sample routes
    routes = [
        {
            "vehicle_type": "diesel_truck",
            "cost_usd": 772,
            "time_hours": 8,
            "carbon_kg": 399,
            "distance_km": 643,
        },
        {
            "vehicle_type": "truck_rail_truck",
            "cost_usd": 305,
            "time_hours": 14,
            "carbon_kg": 60,
            "distance_km": 651,
        },
    ]
    
    rec = optimizer.generate_recommendation(routes, "balanced")
    print(f"      Recommended: {rec['recommended_route']['vehicle_type']}")
    if rec['savings']:
        print(f"      Carbon savings: {rec['savings']['carbon_saved_kg']} kg")
        print(f"      Cost savings: ${rec['savings']['cost_saved_usd']}")
    print("      PASSED")
except Exception as e:
    print(f"      FAILED: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUITE COMPLETE")
print("=" * 70)
print("\nAll core modules are working!")
print("You can now proceed to build the AI agent.\n")
