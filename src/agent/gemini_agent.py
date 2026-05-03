"""
Gemini AI Agent for EcoRoute Optimizer
"""

import re
import sys
from pathlib import Path
from typing import Dict, Optional

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
            raise ImportError("google-generativeai required")
        
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key or self.api_key == "your_gemini_key_here":
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini - IMPORTANT: configure() not Client()
        genai.configure(api_key=self.api_key)
        
        # Create model instance - no 'models/' prefix needed
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✓ Gemini agent initialized with gemini-1.5-flash")
    
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
                # Pattern 3: Simple "X to Y"
                simple_pattern = r'(?:^|\s)([A-Za-z][A-Za-z\s]+?)\s+to\s+([A-Za-z][A-Za-z\s]+?)(?:\s+\d|\s*,|\s*\.|\s*\?|$)'
                match = re.search(simple_pattern, user_message, re.IGNORECASE)
                
                if match:
                    details["origin"] = match.group(1).strip()
                    details["destination"] = match.group(2).strip()
        
        # Extract weight
        weight_pattern = r'(\d+)\s*(?:lbs?|pounds?)'
        weight_match = re.search(weight_pattern, user_message, re.IGNORECASE)
        if weight_match:
            details["weight_lbs"] = int(weight_match.group(1))
        
        return details
    
    def chat_message(self, user_message: str) -> str:
        """Process user message and return response"""
        try:
            # Check if shipping request
            is_shipping = any(word in user_message.lower() 
                            for word in ['ship', 'route', 'send', 'transport', 'deliver', 
                                        'freight', 'lbs', 'pounds', 'from', 'to'])
            
            if is_shipping:
                details = self.extract_shipping_details(user_message)
                
                if details["origin"] and details["destination"]:
                    routes = route_finder.generate_all_routes(
                        origin=details["origin"],
                        destination=details["destination"],
                        weight_lbs=details["weight_lbs"],
                        deadline_hours=details["deadline_hours"]
                    )
                    
                    if not routes:
                        return f"Sorry, couldn't find routes between {details['origin']} and {details['destination']}. Please check city names.\n\nSupported: NYC, LA, SF, Chicago, Boston, and 50+ more."
                    
                    # Format response
                    response = f"I found **{len(routes)} option{'s' if len(routes) > 1 else ''}** from **{details['origin']}** to **{details['destination']}** for **{details['weight_lbs']} lbs**:\n\n---\n\n"
                    
                    for i, route in enumerate(routes, 1):
                        response += f"### Option {i}: {route['vehicle_type'].replace('_', ' ').title()}\n\n"
                        response += f"- **Cost:** ${route['cost_usd']:.0f}\n"
                        response += f"- **Time:** {route['time_hours']:.1f} hours ({route['time_hours']/24:.1f} days)\n"
                        response += f"- **Distance:** {route['distance_km']:.0f} km ({route['distance_km']*0.621371:.0f} miles)\n"
                        response += f"- **Carbon:** {route['carbon_kg']:.0f} kg CO2\n\n"
                    
                    # Add comparison
                    if len(routes) > 1:
                        response += "---\n\n### 💰 Savings Analysis\n\n"
                        baseline = routes[-1]
                        best = routes[0]
                        
                        cost_saved = baseline['cost_usd'] - best['cost_usd']
                        carbon_saved = baseline['carbon_kg'] - best['carbon_kg']
                        
                        if cost_saved > 0:
                            response += f"- **Cost Savings:** ${cost_saved:.0f} ({100*cost_saved/baseline['cost_usd']:.0f}% less)\n"
                            response += f"- **Carbon Reduction:** {carbon_saved:.0f} kg CO2 ({100*carbon_saved/baseline['carbon_kg']:.0f}% cleaner)\n"
                            response += f"- **Impact:** Equivalent to {carbon_saved/21:.0f} trees planted\n\n"
                        
                        response += "### 🎯 Recommendation\n"
                        if best['vehicle_type'] == 'truck_rail_truck':
                            response += "The **intermodal route** offers the best value - dramatically lower cost and emissions."
                        elif best['vehicle_type'] == 'electric_truck':
                            response += "The **electric truck** balances low emissions with speed and flexibility."
                        else:
                            response += f"**{best['vehicle_type'].replace('_', ' ').title()}** is your best option for this route."
                    
                    return response
                else:
                    return "I'd be happy to help! Please provide:\n- Origin city\n- Destination city\n- Weight (optional)\n\nExample: 'Ship 1500 lbs from NYC to LA'"
            
            else:
                # Use Gemini for general questions
                try:
                    prompt = f"""You are a helpful Route Optimization Assistant for EcoRoute Optimizer.

Your capabilities:
- Help users find shipping routes between 60+ US cities
- Compare diesel trucks, electric vehicles, and rail options
- Calculate costs, delivery times, and carbon emissions
- Support cities like NYC, LA, SF, Chicago, Boston, Houston, Miami, Seattle, and 50+ more
- Users can use abbreviations (NYC, LA, SF, etc.)

Be friendly, concise (2-3 sentences), and guide users to try a route query.

User question: {user_message}

Your response:"""

                    response = self.model.generate_content(prompt)
                    return response.text
                    
                except Exception as e:
                    print(f"Gemini error: {e}")
                    return "I'm here to help with shipping routes! Try: 'Ship 1000 lbs from NYC to LA'"
            
        except Exception as e:
            return f"Error: {e}\n\nPlease try again."


# Module-level check
if not GEMINI_AVAILABLE:
    print("Warning: google-generativeai not installed")
