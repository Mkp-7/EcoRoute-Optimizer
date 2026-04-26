"""
Carbon Emissions Calculator for EcoRoute Optimizer
Calculates CO2 emissions based on EPA SmartWay methodology
"""

import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import (
    EMISSIONS_FACTORS,
    WEATHER_IMPACT,
    CARBON_OFFSET_PRICE_PER_TON,
)
from src.utils.helpers import lbs_to_kg


class CarbonCalculator:
    """Calculate carbon emissions for different transport modes"""
    
    def __init__(self):
        self.emissions_factors = EMISSIONS_FACTORS
        self.offset_price = CARBON_OFFSET_PRICE_PER_TON
    
    def calculate_base_emissions(self, distance_km: float, 
                                vehicle_type: str,
                                weight_lbs: float = 0) -> float:
        """
        Calculate base carbon emissions (no adjustments)
        
        Args:
            distance_km: Distance in kilometers
            vehicle_type: 'diesel_truck', 'electric_truck', 'rail', 'intermodal'
            weight_lbs: Shipment weight in pounds (optional, for weight adjustment)
        
        Returns:
            Carbon emissions in kg CO2
        """
        # Get emissions factor (kg CO2 per km)
        emissions_factor = self.emissions_factors.get(vehicle_type, 0.62)
        
        # Base calculation: distance × emissions factor
        base_emissions = distance_km * emissions_factor
        
        # Optional: Adjust for weight (heavier loads = more fuel)
        # Rule: Every 1000 lbs above baseline increases emissions by 5%
        if weight_lbs > 0:
            baseline_weight = 1000  # lbs
            if weight_lbs > baseline_weight:
                excess_weight = weight_lbs - baseline_weight
                weight_multiplier = 1 + (excess_weight / baseline_weight * 0.05)
                base_emissions *= weight_multiplier
        
        return base_emissions
    
    def adjust_for_weather(self, base_emissions: float, 
                          weather_impact: float) -> float:
        """
        Adjust emissions based on weather conditions
        
        Args:
            base_emissions: Base emissions in kg CO2
            weather_impact: Impact factor (e.g., 0.15 = +15%, -0.05 = -5%)
        
        Returns:
            Adjusted emissions in kg CO2
        """
        return base_emissions * (1 + weather_impact)
    
    def adjust_for_grid_carbon(self, electric_vehicle_emissions: float,
                               grid_intensity: float,
                               baseline_intensity: float = 385) -> float:
        """
        Adjust electric vehicle emissions based on grid carbon intensity
        
        Args:
            electric_vehicle_emissions: Base EV emissions (assumes avg grid)
            grid_intensity: Actual grid carbon intensity (gCO2/kWh)
            baseline_intensity: Baseline intensity assumption (default 385 = US avg)
        
        Returns:
            Adjusted emissions in kg CO2
        """
        # Scale emissions based on grid cleanliness
        # If grid is 50% cleaner, emissions are 50% lower
        adjustment_factor = grid_intensity / baseline_intensity
        return electric_vehicle_emissions * adjustment_factor
    
    def calculate_total_emissions(self, distance_km: float,
                                  vehicle_type: str,
                                  weight_lbs: float = 0,
                                  weather_impact: float = 0.0,
                                  grid_intensity: Optional[float] = None) -> Dict:
        """
        Calculate total emissions with all adjustments
        
        Args:
            distance_km: Distance in km
            vehicle_type: Vehicle type
            weight_lbs: Shipment weight in lbs
            weather_impact: Weather impact factor
            grid_intensity: Grid carbon intensity (for EVs)
        
        Returns:
            Dict with emissions breakdown
        """
        # Base emissions
        base = self.calculate_base_emissions(distance_km, vehicle_type, weight_lbs)
        
        # Weather adjustment
        if weather_impact != 0:
            weather_adjusted = self.adjust_for_weather(base, weather_impact)
        else:
            weather_adjusted = base
        
        # Grid adjustment (electric vehicles only)
        if vehicle_type == "electric_truck" and grid_intensity:
            final = self.adjust_for_grid_carbon(weather_adjusted, grid_intensity)
        else:
            final = weather_adjusted
        
        return {
            "base_emissions_kg": round(base, 2),
            "weather_adjusted_kg": round(weather_adjusted, 2),
            "final_emissions_kg": round(final, 2),
            "weather_impact_pct": round(weather_impact * 100, 1),
            "grid_intensity": grid_intensity,
        }
    
    def calculate_offset_cost(self, carbon_kg: float) -> float:
        """
        Calculate cost to offset carbon emissions
        
        Args:
            carbon_kg: Carbon emissions in kg
        
        Returns:
            Offset cost in USD
        """
        tons = carbon_kg / 1000
        return tons * self.offset_price
    
    def calculate_savings(self, route_emissions: float, 
                         baseline_emissions: float) -> Dict:
        """
        Calculate carbon and cost savings vs baseline
        
        Args:
            route_emissions: Proposed route emissions (kg CO2)
            baseline_emissions: Baseline route emissions (kg CO2)
        
        Returns:
            Dict with savings metrics
        """
        carbon_saved = baseline_emissions - route_emissions
        pct_reduction = (carbon_saved / baseline_emissions * 100) if baseline_emissions > 0 else 0
        
        # Cost savings (avoided carbon offset cost)
        cost_saved = self.calculate_offset_cost(carbon_saved)
        
        return {
            "carbon_saved_kg": round(carbon_saved, 2),
            "percent_reduction": round(pct_reduction, 1),
            "offset_cost_saved_usd": round(cost_saved, 2),
        }
    
    def compare_routes(self, routes: list) -> Dict:
        """
        Compare multiple routes and identify best option
        
        Args:
            routes: List of route dicts with 'carbon_kg' key
        
        Returns:
            Dict with comparison metrics
        """
        if not routes:
            return {}
        
        emissions = [r["carbon_kg"] for r in routes]
        
        # Find baseline (usually diesel truck, first option)
        baseline = emissions[0]
        
        # Find best (lowest emissions)
        best_emissions = min(emissions)
        best_index = emissions.index(best_emissions)
        
        # Calculate savings
        savings = self.calculate_savings(best_emissions, baseline)
        
        return {
            "baseline_emissions_kg": round(baseline, 2),
            "best_emissions_kg": round(best_emissions, 2),
            "best_route_index": best_index,
            "savings": savings,
        }


# Singleton instance
calculator = CarbonCalculator()


# Convenience functions
def calculate_emissions(distance_km: float, vehicle_type: str, **kwargs) -> float:
    """Quick emission calculation"""
    result = calculator.calculate_total_emissions(distance_km, vehicle_type, **kwargs)
    return result["final_emissions_kg"]


def calculate_offset(carbon_kg: float) -> float:
    """Quick offset cost calculation"""
    return calculator.calculate_offset_cost(carbon_kg)


# Test function
def test_calculator():
    """Test carbon calculator"""
    print("\n🧪 Testing Carbon Calculator\n")
    
    # Test 1: Basic emissions
    print("1️⃣  Diesel truck - 500 km, 1000 lbs")
    result = calculator.calculate_total_emissions(
        distance_km=500,
        vehicle_type="diesel_truck",
        weight_lbs=1000
    )
    print(f"   Base: {result['base_emissions_kg']} kg CO2")
    print(f"   Final: {result['final_emissions_kg']} kg CO2")
    print(f"   Offset cost: ${calculator.calculate_offset_cost(result['final_emissions_kg']):.2f}\n")
    
    # Test 2: Electric truck with clean grid
    print("2️⃣  Electric truck - 500 km, clean grid (200 gCO2/kWh)")
    result = calculator.calculate_total_emissions(
        distance_km=500,
        vehicle_type="electric_truck",
        weight_lbs=1000,
        grid_intensity=200  # Clean grid (vs 385 US avg)
    )
    print(f"   Final: {result['final_emissions_kg']} kg CO2")
    print(f"   Grid intensity: {result['grid_intensity']} gCO2/kWh\n")
    
    # Test 3: Diesel with headwind
    print("3️⃣  Diesel truck - 500 km, strong headwind")
    result = calculator.calculate_total_emissions(
        distance_km=500,
        vehicle_type="diesel_truck",
        weight_lbs=1000,
        weather_impact=0.15  # +15% fuel due to headwind
    )
    print(f"   Base: {result['base_emissions_kg']} kg CO2")
    print(f"   Weather adjusted: {result['weather_adjusted_kg']} kg CO2")
    print(f"   Weather impact: +{result['weather_impact_pct']}%\n")
    
    # Test 4: Rail (lowest emissions)
    print("4️⃣  Rail - 500 km")
    result = calculator.calculate_total_emissions(
        distance_km=500,
        vehicle_type="rail",
        weight_lbs=1000
    )
    print(f"   Final: {result['final_emissions_kg']} kg CO2\n")
    
    # Test 5: Route comparison
    print("5️⃣  Route Comparison")
    routes = [
        {"name": "Diesel Truck", "carbon_kg": 310},
        {"name": "Electric Truck", "carbon_kg": 90},
        {"name": "Rail", "carbon_kg": 40},
    ]
    comparison = calculator.compare_routes(routes)
    print(f"   Baseline: {comparison['baseline_emissions_kg']} kg CO2 (Diesel)")
    print(f"   Best option: {comparison['best_emissions_kg']} kg CO2 (Rail)")
    print(f"   Savings: {comparison['savings']['carbon_saved_kg']} kg CO2 "
          f"({comparison['savings']['percent_reduction']}% reduction)")
    print(f"   Offset cost saved: ${comparison['savings']['offset_cost_saved_usd']:.2f}\n")
    
    print("✅ Carbon calculator tests complete!\n")


if __name__ == "__main__":
    test_calculator()
