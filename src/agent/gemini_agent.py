"""
Gemini AI Agent for EcoRoute Optimizer
Compatible with google-genai v1.73.1+
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try new import (v1.73.1+)
try:
    from google.genai import Client
    GEMINI_AVAILABLE = True
    print("✓ Gemini package loaded successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"✗ Failed to import Gemini: {e}")

from config.settings import GEMINI_API_KEY
from src.routing.route_finder import route_finder
from src.routing.optimizer import optimizer


class GeminiRouteAgent:
    """AI Agent using Google Gemini (Free tier)"""
    
    def __init__(self, api_key: str = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai package required. Install with: pip install google-genai")
        
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key or self.api_key == "your_gemini_key_here" or not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
        
        # Initialize Gemini client
        self.client = Client(api_key=self.api_key)
        # Use models.generate_content compatible model name
        self.model_name = 'models/gemini-1.5-flash-latest'
        
        print(f"✓ Gemini agent initialized with model: {self.model_name}")
    
    def extract_shipping_details(self, user_message: str) -> Dict:
        """Extract shipping details from user message"""
        details = {
            "origin": None,
            "destination": None,
            "weight_lbs": 1000,
            "deadline_hours": None
        }
        
        # Simple pattern matching
        # Look for "from X to Y" or "X to Y"
        from_to_pattern = r'from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|,|\.|\?|$)'
        match = re.search(from_to_pattern, user_message, re.IGNORECASE)
        
        if match:
            details["origin"] = match.group(1).strip()
            details["destination"] = match.group(2).strip()
        
        # Look for weight
        weight_pattern = r'(\d+)\s*(?:lbs?|pounds?)'
        weight_match = re.search(weight_pattern, user_message, re.IGNORECASE)
        if weight_match:
            details["weight_lbs"] = int(weight_match.group(1))
        
        return details
    
    def chat_message(self, user_message: str) -> str:
        """
        Process user message and return response
        
        Args:
            user_message: User's question/request
        
        Returns:
            Response text
        """
        try:
            # Check if this is a shipping request
            is_shipping_query = any(word in user_message.lower() 
                                   for word in ['ship', 'route', 'send', 'transport', 'deliver', 'freight', 
                                               'lbs', 'pounds', 'from', 'to'])
            
            if is_shipping_query:
                # Extract details
                details = self.extract_shipping_details(user_message)
                
                if details["origin"] and details["destination"]:
                    # Generate routes
                    print(f"\n[Generating routes: {details['origin']} to {details['destination']}]")
                    
                    routes = route_finder.generate_all_routes(
                        origin=details["origin"],
                        destination=details["destination"],
                        weight_lbs=details["weight_lbs"],
                        deadline_hours=details["deadline_hours"]
                    )
                    
                    if not routes:
                        return f"Sorry, I couldn't find routes between {details['origin']} and {details['destination']}. Please check the city names and try again.\n\nSupported cities include: New York, Los Angeles, Chicago, San Francisco, Miami, Seattle, and 40+ more."
                    
                    # Format response with proper markdown
                    response = f"I found **{len(routes)} shipping option{'s' if len(routes) > 1 else ''}** from **{details['origin']}** to **{details['destination']}** for **{details['weight_lbs']} lbs**:\n\n"
                    
                    response += "---\n\n"
                    
                    for i, route in enumerate(routes, 1):
                        response += f"### Option {i}: {route['vehicle_type'].replace('_', ' ').title()}\n\n"
                        response += f"- **Cost:** ${route['cost_usd']:.0f}\n"
                        response += f"- **Time:** {route['time_hours']:.1f} hours ({route['time_hours']/24:.1f} days)\n"
                        response += f"- **Distance:** {route['distance_km']:.0f} km ({route['distance_km']*0.621371:.0f} miles)\n"
                        response += f"- **Carbon:** {route['carbon_kg']:.0f} kg CO2\n"
                        
                        # Add route details for intermodal
                        if 'origin_hub' in route and 'dest_hub' in route:
                            response += f"- **Route:** Truck to {route['origin_hub'].title()} rail hub → Train to {route['dest_hub'].title()} → Truck to destination\n"
                        
                        response += "\n"
                    
                    # Add detailed comparison if multiple routes
                    if len(routes) > 1:
                        response += "---\n\n"
                        baseline = routes[-1]  # Diesel is usually last
                        best = routes[0]  # Best option (lowest carbon)
                        
                        cost_saved = baseline['cost_usd'] - best['cost_usd']
                        carbon_saved = baseline['carbon_kg'] - best['carbon_kg']
                        time_diff = best['time_hours'] - baseline['time_hours']
                        
                        response += "### 💰 Savings Analysis\n\n"
                        response += f"- **Cost Savings:** ${cost_saved:.0f} ({cost_saved/baseline['cost_usd']*100:.0f}% less than diesel)\n"
                        response += f"- **Carbon Reduction:** {carbon_saved:.0f} kg CO2 ({carbon_saved/baseline['carbon_kg']*100:.0f}% cleaner)\n"
                        
                        # Add context
                        trees = carbon_saved / 21  # 21 kg CO2 per tree per year
                        cars = carbon_saved / 4.6  # 4.6 kg CO2 per gallon gas
                        response += f"- **Environmental Impact:** Equivalent to **{trees:.0f} trees** planted or **{cars:.0f} gallons** of gas saved\n"
                        
                        if time_diff > 0:
                            response += f"- **Trade-off:** Takes {time_diff:.0f} hours longer ({time_diff/24:.1f} extra days)\n"
                        
                        response += "\n"
                    
                    # Add recommendation with reasoning
                    response += "---\n\n"
                    best = routes[0]
                    response += "### 🎯 Recommendation\n\n"
                    
                    if best['vehicle_type'] == 'truck_rail_truck':
                        response += f"The **intermodal (rail) route** is your best option. Here's why:\n\n"
                        response += f"1. **Cost-Effective:** At ${best['cost_usd']:.0f}, it's significantly cheaper than diesel trucking\n"
                        response += f"2. **Environmentally Superior:** Rail is 3-4x more carbon-efficient than trucks\n"
                        response += f"3. **Scalable:** Rail can handle large volumes economically\n\n"
                        
                        if len(routes) > 1:
                            response += f"While it takes **{best['time_hours'] - routes[-1]['time_hours']:.0f} hours longer**, the massive cost and carbon savings make it the clear winner for most shipments. "
                            response += f"Unless you have an urgent deadline, intermodal is the smart choice."
                    
                    elif best['vehicle_type'] == 'electric_truck':
                        response += f"The **electric truck** offers the best balance - lower emissions than diesel while maintaining speed and flexibility."
                    
                    else:
                        response += f"For this route and timeframe, **{best['vehicle_type'].replace('_', ' ')}** is your best option."
                    
                    return response
                else:
                    # Ask for missing details
                    return "I'd be happy to help you find shipping routes! Please provide:\n- Origin city\n- Destination city\n- Weight (optional, defaults to 1000 lbs)\n\nExample: 'Ship 1500 lbs from New York to Los Angeles'"
            
            else:
                # General question - use Gemini to answer
                # For now, just extract if it's a shipping query
                return "I'm optimized for shipping route queries! Please ask me to find routes between cities.\n\nExample: 'Ship 1500 lbs from San Francisco to Chicago'"
            
        except Exception as e:
            return f"Error: {str(e)}\n\nPlease try again or rephrase your question."
    
    def reset_conversation(self):
        """Reset (not needed with stateless approach)"""
        pass


# Test function
def test_gemini_agent():
    """Test the Gemini AI agent"""
    
    print("\nTESTING GEMINI AI AGENT")
    print("=" * 70)
    print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
    
    if not GEMINI_AVAILABLE:
        print("\n✗ google-genai package not available")
        print("Install with: pip install google-genai")
        return
    
    try:
        print("\nInitializing agent...")
        agent = GeminiRouteAgent()
    except ValueError as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease set your Gemini API key in .env file:")
        print("GEMINI_API_KEY=AIza-your-key-here")
        print("\nGet a free key at: https://aistudio.google.com/app/apikey")
        return
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test query
    print("\nUser Query:")
    print("-" * 70)
    query = "Ship 1500 lbs from San Francisco to Chicago"
    print(query)
    
    print("\n\nGemini's Response:")
    print("-" * 70)
    
    response = agent.chat_message(query)
    print(response)
    
    print("\n" + "=" * 70)
    print("✓ GEMINI AGENT TEST COMPLETE\n")


if __name__ == "__main__":
    test_gemini_agent()
