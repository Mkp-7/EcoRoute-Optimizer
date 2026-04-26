"""
Multi-Objective Optimizer for EcoRoute
Ranks routes by cost, time, and carbon emissions
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.carbon.calculator import calculator


class RouteOptimizer:
    """Optimize and rank routes across multiple objectives"""
    
    def __init__(self):
        pass
    
    def calculate_pareto_frontier(self, routes: List[Dict]) -> List[Dict]:
        """
        Find Pareto-optimal routes (non-dominated solutions)
        
        A route is Pareto-optimal if no other route is better in ALL dimensions
        
        Args:
            routes: List of route dicts
        
        Returns:
            List of Pareto-optimal routes
        """
        if not routes:
            return []
        
        pareto_routes = []
        
        for route in routes:
            is_dominated = False
            
            # Check if this route is dominated by any other route
            for other in routes:
                if route == other:
                    continue
                
                # Check if 'other' dominates 'route'
                # (better or equal in all dimensions, strictly better in at least one)
                cost_better = other['cost_usd'] <= route['cost_usd']
                time_better = other['time_hours'] <= route['time_hours']
                carbon_better = other['carbon_kg'] <= route['carbon_kg']
                
                # At least one strictly better
                cost_strictly_better = other['cost_usd'] < route['cost_usd']
                time_strictly_better = other['time_hours'] < route['time_hours']
                carbon_strictly_better = other['carbon_kg'] < route['carbon_kg']
                
                if (cost_better and time_better and carbon_better and
                    (cost_strictly_better or time_strictly_better or carbon_strictly_better)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_routes.append(route)
        
        return pareto_routes
    
    def rank_by_preference(self, routes: List[Dict], 
                          preference: str = "balanced") -> List[Dict]:
        """
        Rank routes by user preference
        
        Args:
            routes: List of route dicts
            preference: 'cost', 'time', 'carbon', or 'balanced'
        
        Returns:
            Sorted list of routes
        """
        if not routes:
            return []
        
        if preference == "cost":
            # Sort by cost (lowest first)
            return sorted(routes, key=lambda r: r['cost_usd'])
        
        elif preference == "time":
            # Sort by time (fastest first)
            return sorted(routes, key=lambda r: r['time_hours'])
        
        elif preference == "carbon":
            # Sort by carbon (greenest first)
            return sorted(routes, key=lambda r: r['carbon_kg'])
        
        else:  # balanced
            # Normalize each dimension to 0-1 scale
            costs = [r['cost_usd'] for r in routes]
            times = [r['time_hours'] for r in routes]
            carbons = [r['carbon_kg'] for r in routes]
            
            cost_min, cost_max = min(costs), max(costs)
            time_min, time_max = min(times), max(times)
            carbon_min, carbon_max = min(carbons), max(carbons)
            
            # Avoid division by zero
            cost_range = cost_max - cost_min if cost_max != cost_min else 1
            time_range = time_max - time_min if time_max != time_min else 1
            carbon_range = carbon_max - carbon_min if carbon_max != carbon_min else 1
            
            # Calculate composite score (lower is better)
            scores = []
            for route in routes:
                cost_score = (route['cost_usd'] - cost_min) / cost_range
                time_score = (route['time_hours'] - time_min) / time_range
                carbon_score = (route['carbon_kg'] - carbon_min) / carbon_range
                
                # Weighted average (equal weights for balanced)
                composite = (cost_score + time_score + carbon_score) / 3
                scores.append((composite, route))
            
            # Sort by composite score
            scores.sort(key=lambda x: x[0])
            return [route for score, route in scores]
    
    def calculate_savings(self, route: Dict, baseline: Dict) -> Dict:
        """
        Calculate savings vs baseline route
        
        Args:
            route: Route to compare
            baseline: Baseline route (usually diesel truck)
        
        Returns:
            Dict with savings metrics
        """
        carbon_savings = calculator.calculate_savings(
            route['carbon_kg'],
            baseline['carbon_kg']
        )
        
        cost_saved = baseline['cost_usd'] - route['cost_usd']
        cost_pct = (cost_saved / baseline['cost_usd'] * 100) if baseline['cost_usd'] > 0 else 0
        
        time_diff = route['time_hours'] - baseline['time_hours']
        time_pct = (time_diff / baseline['time_hours'] * 100) if baseline['time_hours'] > 0 else 0
        
        return {
            "carbon_saved_kg": carbon_savings['carbon_saved_kg'],
            "carbon_percent_reduction": carbon_savings['percent_reduction'],
            "cost_saved_usd": round(cost_saved, 2),
            "cost_percent_saved": round(cost_pct, 1),
            "time_difference_hours": round(time_diff, 1),
            "time_percent_difference": round(time_pct, 1),
        }
    
    def generate_recommendation(self, routes: List[Dict], 
                               preference: str = "balanced") -> Dict:
        """
        Generate route recommendation with reasoning
        
        Args:
            routes: List of route options
            preference: User preference
        
        Returns:
            Dict with recommendation and reasoning
        """
        if not routes:
            return {
                "recommended_route": None,
                "reasoning": "No viable routes found",
                "alternatives": []
            }
        
        # Rank routes by preference
        ranked = self.rank_by_preference(routes, preference)
        
        # Best route
        best = ranked[0]
        
        # Baseline (diesel truck) for comparison
        baseline = next((r for r in routes if r['vehicle_type'] == 'diesel_truck'), routes[0])
        
        # Calculate savings vs baseline
        if best != baseline:
            savings = self.calculate_savings(best, baseline)
        else:
            savings = None
        
        # Generate reasoning
        reasoning = self._generate_reasoning(best, baseline, savings, preference)
        
        # Pareto frontier
        pareto = self.calculate_pareto_frontier(routes)
        
        return {
            "recommended_route": best,
            "baseline_route": baseline,
            "savings": savings,
            "reasoning": reasoning,
            "all_routes": ranked,
            "pareto_optimal": pareto,
            "preference": preference,
        }
    
    def _generate_reasoning(self, route: Dict, baseline: Dict, 
                           savings: Optional[Dict], preference: str) -> str:
        """Generate human-readable reasoning for recommendation"""
        
        if route == baseline:
            return (f"The diesel truck route is your only viable option, "
                   f"costing ${route['cost_usd']:.0f} and taking {route['time_hours']:.1f} hours.")
        
        mode_name = route['vehicle_type'].replace('_', ' ').title()
        
        if preference == "cost":
            reason = (f"The {mode_name} route offers the best value at ${route['cost_usd']:.0f}, "
                     f"saving ${savings['cost_saved_usd']:.0f} ({savings['cost_percent_saved']:.0f}%) "
                     f"compared to diesel truck.")
        
        elif preference == "time":
            reason = (f"The {mode_name} route is fastest at {route['time_hours']:.1f} hours.")
        
        elif preference == "carbon":
            reason = (f"The {mode_name} route is greenest with {route['carbon_kg']:.0f} kg CO2, "
                     f"reducing emissions by {savings['carbon_saved_kg']:.0f} kg "
                     f"({savings['carbon_percent_reduction']:.0f}%) vs diesel.")
        
        else:  # balanced
            reason = (f"The {mode_name} route offers the best overall balance. "
                     f"It saves ${savings['cost_saved_usd']:.0f} ({savings['cost_percent_saved']:.0f}%) "
                     f"and reduces carbon by {savings['carbon_saved_kg']:.0f} kg "
                     f"({savings['carbon_percent_reduction']:.0f}%), "
                     f"though it takes {abs(savings['time_difference_hours']):.1f} hours "
                     f"{'longer' if savings['time_difference_hours'] > 0 else 'less'}.")
        
        return reason


# Singleton instance
optimizer = RouteOptimizer()


# Test function
def test_optimizer():
    """Test optimizer with sample routes"""
    print("\nTESTING ROUTE OPTIMIZER\n")
    print("=" * 70)
    
    # Sample routes (SF to Chicago)
    routes = [
        {
            "vehicle_type": "diesel_truck",
            "cost_usd": 4119,
            "time_hours": 43,
            "carbon_kg": 2181,
            "distance_km": 3433,
        },
        {
            "vehicle_type": "truck_rail_truck",
            "cost_usd": 1556,
            "time_hours": 57,
            "carbon_kg": 290,
            "distance_km": 3433,
        },
    ]
    
    # Test 1: Pareto Frontier
    print("\n1. PARETO FRONTIER:")
    print("-" * 70)
    pareto = optimizer.calculate_pareto_frontier(routes)
    print(f"Found {len(pareto)} Pareto-optimal routes:")
    for route in pareto:
        print(f"   - {route['vehicle_type']}: "
              f"${route['cost_usd']}, {route['time_hours']}hrs, {route['carbon_kg']} kg CO2")
    
    # Test 2: Rank by Different Preferences
    print("\n2. RANKING BY PREFERENCE:")
    print("-" * 70)
    
    for pref in ["cost", "time", "carbon", "balanced"]:
        ranked = optimizer.rank_by_preference(routes, pref)
        best = ranked[0]
        print(f"\n{pref.upper()} preference:")
        print(f"   Winner: {best['vehicle_type']}")
        print(f"   Cost: ${best['cost_usd']}, Time: {best['time_hours']}hrs, "
              f"Carbon: {best['carbon_kg']} kg CO2")
    
    # Test 3: Generate Recommendation
    print("\n3. RECOMMENDATION (Balanced Preference):")
    print("-" * 70)
    
    rec = optimizer.generate_recommendation(routes, "balanced")
    print(f"\nRecommended: {rec['recommended_route']['vehicle_type']}")
    print(f"\nReasoning:")
    print(f"   {rec['reasoning']}")
    
    if rec['savings']:
        print(f"\nSavings vs Baseline:")
        print(f"   Cost: ${rec['savings']['cost_saved_usd']} "
              f"({rec['savings']['cost_percent_saved']}%)")
        print(f"   Carbon: {rec['savings']['carbon_saved_kg']} kg "
              f"({rec['savings']['carbon_percent_reduction']}%)")
        print(f"   Time: {rec['savings']['time_difference_hours']}hrs "
              f"({rec['savings']['time_percent_difference']}%)")
    
    print("\n" + "=" * 70)
    print("OPTIMIZER TESTS COMPLETE!\n")


if __name__ == "__main__":
    test_optimizer()
