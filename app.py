"""
EcoRoute Optimizer - Streamlit Web Interface
AI-Powered Carbon-Optimized Logistics Platform
"""

import streamlit as st
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
try:
    from src.agent.gemini_agent import GeminiRouteAgent, GEMINI_AVAILABLE
    from src.routing.route_finder import route_finder
    from src.carbon.calculator import calculator
    from src.utils.helpers import format_currency, format_carbon, calculate_trees_equivalent
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure all dependencies are installed: pip install -r requirements.txt")
    st.stop()

AI_AVAILABLE = GEMINI_AVAILABLE
AI_NAME = "Gemini"

# Page config
st.set_page_config(
    page_title="EcoRoute Optimizer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .route-card {
        background: #f0f7f0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin: 1rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌱 EcoRoute Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Carbon-Optimized Shipping Routes</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Mode selection
    mode = st.radio(
        "Choose Mode:",
        ["🤖 AI Chat Assistant", "📊 Route Comparison"],
        help="AI Chat uses LLM to understand natural language. Route Comparison shows all options."
    )
    
    st.markdown("---")
    
    st.subheader("📍 Supported Cities")
    st.markdown("""
    **NYC Metro:** Manhattan, Brooklyn, Queens, Bronx, Newark, Jersey City, Passaic, Clifton
    
    **Major Cities:** San Francisco, Los Angeles, Chicago, Houston, Boston, Seattle, Miami, and 40+ more
    
    [See full list](https://github.com/Mkp-7/EcoRoute-Optimizer#-supported-cities)
    """)
    
    st.markdown("---")
    
    st.subheader("ℹ️ About")
    st.info("""
    This platform optimizes shipping routes by balancing:
    - 💰 Cost
    - ⏱️ Delivery Time  
    - 🌱 Carbon Emissions
    
    **Proven Savings:**
    - 60-87% carbon reduction
    - 50-62% cost savings
    """)

# Main content
if mode == "🤖 AI Chat Assistant":
    st.header(f"💬 Hi I am your Route Assistant!")
    
    # Check if AI is available
    if not AI_AVAILABLE:
        st.error("Google Gemini package not installed. Install with: `pip install google-genai`")
        st.info("Gemini is 100% FREE with generous rate limits!")
        st.code("pip install google-genai", language="bash")
        st.stop()
    
    # Initialize agent
    if 'agent' not in st.session_state:
        try:
            st.session_state.agent = GeminiRouteAgent()
            st.session_state.messages = []
        except Exception as e:
            st.error(f"Error initializing AI agent: {e}")
            st.info("Make sure your GEMINI_API_KEY is set in .env file")
            st.info("Get a free key at: https://aistudio.google.com/app/apikey")
            st.stop()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about shipping routes... (e.g., 'Ship 1000 lbs from NYC to LA')"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.chat_message(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")

else:  # Route Comparison Mode
    st.header("📊 Route Comparison Tool")
    
    # Input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        origin = st.text_input("Origin City", placeholder="e.g., San Francisco")
    
    with col2:
        destination = st.text_input("Destination City", placeholder="e.g., Chicago")
    
    with col3:
        weight = st.number_input("Weight (lbs)", min_value=100, max_value=50000, value=1000, step=100)
    
    # Optional parameters
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            deadline = st.number_input("Deadline (hours)", min_value=0, value=0, help="Leave at 0 for no deadline")
        with col2:
            preference = st.selectbox("Optimization Priority", ["Balanced", "Cost", "Time", "Carbon"])
    
    # Generate routes button
    if st.button("🔍 Find Routes", type="primary", use_container_width=True):
        if not origin or not destination:
            st.warning("Please enter both origin and destination cities")
        else:
            with st.spinner("Generating optimal routes..."):
                try:
                    # Generate routes
                    routes = route_finder.generate_all_routes(
                        origin=origin,
                        destination=destination,
                        weight_lbs=weight,
                        deadline_hours=deadline if deadline > 0 else None
                    )
                    
                    if not routes:
                        st.error(f"No routes found. Please check city names. Supported cities: San Francisco, Los Angeles, New York, Chicago, etc.")
                    else:
                        st.success(f"Found {len(routes)} route options!")
                        
                        # Display routes
                        for i, route in enumerate(routes, 1):
                            with st.container():
                                st.markdown(f"### Option {i}: {route['vehicle_type'].replace('_', ' ').title()}")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("💰 Cost", f"${route['cost_usd']:.0f}")
                                
                                with col2:
                                    st.metric("⏱️ Time", f"{route['time_hours']:.1f} hrs")
                                
                                with col3:
                                    st.metric("📏 Distance", f"{route['distance_km']:.0f} km")
                                
                                with col4:
                                    st.metric("🌱 Carbon", f"{route['carbon_kg']:.0f} kg CO2")
                                
                                # Carbon context
                                trees = calculate_trees_equivalent(route['carbon_kg'])
                                st.caption(f"🌳 Equivalent to {trees:.1f} trees planted")
                                
                                # Savings vs baseline
                                if i > 1:
                                    baseline = routes[0]
                                    cost_saved = baseline['cost_usd'] - route['cost_usd']
                                    carbon_saved = baseline['carbon_kg'] - route['carbon_kg']
                                    
                                    if carbon_saved > 0:
                                        st.success(f"✅ Saves ${cost_saved:.0f} ({cost_saved/baseline['cost_usd']*100:.0f}%) and {carbon_saved:.0f} kg CO2 ({carbon_saved/baseline['carbon_kg']*100:.0f}%) vs diesel truck")
                                
                                st.markdown("---")
                        
                        # Recommendation
                        st.subheader("💡 Recommendation")
                        best_route = routes[0]  # Already sorted by carbon
                        
                        if preference.lower() == "cost":
                            best_route = min(routes, key=lambda r: r['cost_usd'])
                        elif preference.lower() == "time":
                            best_route = min(routes, key=lambda r: r['time_hours'])
                        
                        st.info(f"""
                        **Best Option:** {best_route['vehicle_type'].replace('_', ' ').title()}
                        
                        - Cost: ${best_route['cost_usd']:.0f}
                        - Time: {best_route['time_hours']:.1f} hours
                        - Carbon: {best_route['carbon_kg']:.0f} kg CO2
                        
                        {best_route.get('route_description', '')}
                        """)
                
                except Exception as e:
                    st.error(f"Error generating routes: {e}")
                    st.info("Please check that cities are spelled correctly and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    Built with ❤️ for sustainable logistics ♻️
</div>
""", unsafe_allow_html=True)
