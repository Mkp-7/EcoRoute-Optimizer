"""
Gemini AI Agent for EcoRoute Optimizer
Uses google-generativeai library
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed")

from config.settings import GEMINI_API_KEY
from src.routing.route_finder import route_finder


class GeminiRouteAgent:
    """AI Agent using Google Gemini"""
    
    def __init__(self, api_key: str = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai required. Install: pip install google-generativeai")
        
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key or self.api_key == "your_gemini_key_here":
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print(f"✓ Gemini agent initialized with model: gemini-1.5-flash")
    
    def extract_shipping_details(self, user_message: str) -> Dict:
        """Extract shipping details from user message"""
        details = {
            "origin": None,
            "destination": None,
            "weight_lbs": 1000,
            "deadline_hours": None
        }
        
        # Pattern 1: "from X to Y"
        from_to_pattern = r'from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+\d|\s*,|\s*\.|\s*\?|$)'
        match = re.search(from_to_pattern, user_message, re.IGNORECASE)
        
        if match:
            details["origin"] = match.group(1).strip()
            details["destination"] = match.group(2).strip()
        else:
            # Pattern 2: "to Y from X"
            to_from_pattern = r'to\s+([A-Za-z\s]+?)\s+from\s+([A-Za-z\s]+?)(?:\s+\d|\s*,|\s*\.|\s*\?|$)'
            match = re.search(to_from_pattern, user_message, re.IGNORECASE)
            
            if match:
                details["destination"] = match.group(1).strip()
                details["origin"] = match.group(2).strip()
            else:
                # Pattern 3: "X to Y"
                simple_pattern = r'(?:^|\s)([A-Za-z][A-Za-z\s]+?)\s+to\s+([A-Za-z][A-Za-z\s]+?)(?:\s+\d|\s*,|\s*\.|\s*\?|$)'
                match = re.search(simple_pattern, user_message, re.IGNORECASE)
                
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
                    
                    # Format response
                    response = f"I found **{len(routes)} shipping option{'s' if len(routes) > 1 else ''}** from **{details['origin']}** to **{details['destination']}** for **{details['weight_lbs']} lbs**:\n\n"
                    
                    response += "---\n\n"
                    
                    for i, route in enumerate(routes, 1):
                        response += f"### Option {i}: {route['vehicle_type'].replace('_', ' ').title()}\n\n"
                        response += f"- **Cost:** ${route['cost_usd']:.0f}\n"
                        response += f"- **Time:** {route['time_hours']:.1f} hours ({route['time_hours']/24:.1f} days)\n"
                        response += f"- **Distance:** {route['distance_km']:.0f} km ({route['distance_km']*0.621371:.0f} miles)\n"
                        response += f"- **Carbon:** {route['carbon_kg']:.0f} kg CO2\n\n"
                    
                    # Add comparison if multiple routes
                    if len(routes) > 1:
                        response += "---\n\n"
                        baseline = routes[-1]
                        best = routes[0]
                        
                        cost_saved = baseline['cost_usd'] - best['cost_usd']
                        carbon_saved = baseline['carbon_kg'] - best['carbon_kg']
                        
                        if cost_saved > 0:
                            response += f"### 💰 Savings Analysis\n\n"
                            response += f"- **Cost Savings:** ${cost_saved:.0f} ({100*cost_saved/baseline['cost_usd']:.0f}% less than diesel)\n"
                            response += f"- **Carbon Reduction:** {carbon_saved:.0f} kg CO2 ({100*carbon_saved/baseline['carbon_kg']:.0f}% cleaner)\n"
                            response += f"- **Environmental Impact:** Equivalent to {carbon_saved/21:.0f} trees planted or {carbon_saved/8.89:.0f} gallons of gas saved\n\n"
                        
                        response += "### 🎯 Recommendation\n"
                        if best['vehicle_type'] == 'truck_rail_truck':
                            response += f"The **intermodal route** offers the best value - dramatically lower cost and emissions. "
                        elif best['vehicle_type'] == 'electric_truck':
                            response += f"The **electric truck** offers the best balance - lower emissions than diesel while maintaining speed and flexibility."
                        else:
                            response += f"For this route, **{best['vehicle_type'].replace('_', ' ')}** is your best option."
                    
                    return response
                else:
                    return "I'd be happy to help you find shipping routes! Please provide:\n- Origin city\n- Destination city\n- Weight (optional, defaults to 1000 lbs)\n\nExample: 'Ship 1500 lbs from New York to Los Angeles'"
            
            else:
                # Use Gemini AI for general conversation
                try:
                    prompt = f"""You are a helpful Route Optimization Assistant for EcoRoute Optimizer.

Your capabilities:
- You help users find shipping routes between 60+ US cities
- You compare diesel trucks, electric vehicles, and intermodal rail options
- You calculate costs, delivery times, and carbon emissions
- You support cities like NYC, LA, SF, Chicago, Boston, Houston, Miami, Atlanta, Seattle, and 50+ more
- Users can use abbreviations (NYC, LA, SF, etc.)

When users ask general questions:
- Be friendly and helpful
- Explain your capabilities clearly
- If they ask about cities, mention you support 60+ major US cities including NYC metro (Manhattan, Brooklyn, Queens, Newark, Jersey City), California (SF, LA, San Diego, San Jose), and major metros across the US
- If they ask what you can do, explain you compare shipping routes to find the best balance of cost, time, and carbon emissions
- Always be concise and conversational (2-3 sentences max)
- Guide them toward trying a route query like "Ship 1000 lbs from NYC to LA"

User question: {user_message}

Your response (keep it brief and friendly):"""

                    response = self.model.generate_content(prompt)
                    return response.text
                    
                except Exception as e:
                    print(f"[ERROR] Gemini API error: {str(e)}")
                    return f"Gemini API Error: {str(e)}"
            
        except Exception as e:
            return f"Error: {str(e)}\n\nPlease try again or rephrase your question."


# Check if available on import
if not GEMINI_AVAILABLE:
    print("\n✗ google-generativeai package not available")
    print("Install with: pip install google-generativeai")
