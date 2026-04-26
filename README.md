# GreenRoute AI - Carbon-Optimized Logistics Agent

## 🌍 Overview

GreenRoute AI is an agentic AI system that optimizes logistics routing by balancing **cost**, **delivery time**, and **carbon emissions**. Built with Claude API and real-time environmental data, it helps logistics companies meet ESG goals while maintaining operational efficiency.

### Key Features
- **Multi-objective optimization**: Balances cost, time, and carbon footprint
- **Real-time carbon intensity data**: Uses live grid emissions data for routing decisions
- **Agentic reasoning**: Claude AI explains trade-offs and recommends optimal routes
- **Intermodal routing**: Evaluates truck, rail, and combined transport options
- **Weather-aware**: Adjusts fuel estimates based on wind and temperature
- **Compliance reporting**: Auto-generates Scope 3 emissions reports
- **Carbon offset calculator**: Calculates and tracks offset costs

### Why This Matters
- **Regulatory compliance**: Scope 3 emissions reporting required by 2027
- **Cost savings**: Intermodal routing often cheaper AND greener (15-25% carbon reduction)
- **Competitive advantage**: First AI-driven carbon optimization for logistics
- **Market demand**: Enterprise customers need ESG solutions

---

## 🛠️ Tech Stack

- **AI Agent**: Claude Sonnet 4 (Anthropic API)
- **Backend**: Python 3.10+
- **Database**: SQLite (local caching)
- **APIs**: 
  - Electricity Map (carbon intensity)
  - Carbon Interface (emissions calculation)
  - OpenRouteService (routing)
  - OpenWeatherMap (weather data)
- **UI**: Streamlit
- **Libraries**: pandas, requests, plotly, geopy

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- API keys (free tier):
  - Anthropic API key
  - Electricity Map API key
  - Carbon Interface API key
  - OpenRouteService API key
  - OpenWeatherMap API key

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/greenroute-ai.git
cd greenroute-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_db.py

# Load sample data
python scripts/load_sample_data.py

# Run the application
streamlit run app.py
```

---

## 🎯 Quick Start

1. **Enter shipment details**: Origin, destination, weight, deadline
2. **Set preferences**: Cost-focused, time-focused, or carbon-focused
3. **Get AI recommendations**: Agent analyzes routes and suggests optimal option
4. **View impact**: See carbon savings, cost comparison, and sustainability metrics
5. **Export report**: Download compliance-ready emissions report

---

## 📊 Example Results

**Scenario**: 1000 lbs from San Francisco to Chicago, 3-day deadline

| Route Option | Cost | Time | Carbon | Savings |
|-------------|------|------|--------|---------|
| Diesel Truck | $350 | 22hrs | 145 kg | Baseline |
| Electric Truck | $385 | 26hrs | 42 kg | 71% ↓ |
| Intermodal | $320 | 48hrs | 38 kg | 74% ↓ |

**AI Recommendation**: Intermodal (lowest cost + lowest carbon)

---

## 🗂️ Project Structure

```
greenroute-ai/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── config/
│   └── settings.py            # Configuration management
│
├── data/
│   ├── greenroute.db          # SQLite database
│   └── sample_routes.csv      # Sample route data
│
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── claude_agent.py    # Claude API integration
│   │   └── prompts.py         # System prompts for agent
│   │
│   ├── carbon/
│   │   ├── __init__.py
│   │   ├── calculator.py      # Emissions calculations
│   │   └── intensity.py       # Grid carbon intensity API
│   │
│   ├── routing/
│   │   ├── __init__.py
│   │   ├── route_finder.py    # Route generation logic
│   │   └── optimizer.py       # Multi-objective optimization
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── database.py        # Database operations
│   │
│   └── utils/
│       ├── __init__.py
│       ├── api_clients.py     # External API wrappers
│       └── helpers.py         # Utility functions
│
├── scripts/
│   ├── init_db.py             # Database initialization
│   └── load_sample_data.py    # Load demo data
│
└── tests/
    ├── __init__.py
    ├── test_agent.py
    ├── test_carbon.py
    └── test_routing.py
```

---

## 🔑 API Keys Setup

### Free Tier Limits (All APIs)
- **Anthropic Claude**: $5 free credit (thousands of requests)
- **Electricity Map**: 50 requests/day
- **Carbon Interface**: 200 requests/month
- **OpenRouteService**: 2000 requests/day
- **OpenWeatherMap**: 1000 requests/day

### Getting API Keys

1. **Anthropic Claude**:
   - Sign up at https://console.anthropic.com
   - Navigate to API Keys
   - Create new key

2. **Electricity Map**:
   - Sign up at https://api-portal.electricitymaps.com
   - Free tier: 50 requests/day

3. **Carbon Interface**:
   - Sign up at https://www.carboninterface.com
   - Free tier: 200 requests/month

4. **OpenRouteService**:
   - Sign up at https://openrouteservice.org/dev/#/signup
   - Free tier: 2000 requests/day

5. **OpenWeatherMap**:
   - Sign up at https://home.openweathermap.org/users/sign_up
   - Free tier: 1000 requests/day

---

## 🎬 Demo

[Link to demo video - to be added]

[Link to live deployment - to be added]

---

## 📈 Roadmap

### Phase 1 (Current - Week 1-2)
- [x] Project structure
- [ ] Core routing engine
- [ ] Carbon calculations
- [ ] Claude agent integration
- [ ] Basic Streamlit UI

### Phase 2 (Week 3-4)
- [ ] Advanced visualizations
- [ ] Multi-modal routing (rail integration)
- [ ] Weather impact modeling
- [ ] Compliance report generation

### Phase 3 (Future)
- [ ] Real carrier API integrations
- [ ] Historical optimization tracking
- [ ] ML-based demand prediction
- [ ] Mobile app

---

## 🤝 Contributing

This is currently a portfolio/demonstration project. Contributions welcome after initial release.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Mukund Patel**
- LinkedIn: [Your LinkedIn]
- GitHub: [@mkpatel4102](https://github.com/mkpatel4102)
- Email: mkpatel4102@gmail.com

---

## 🙏 Acknowledgments

- Orchestro.ai for inspiration
- Anthropic for Claude API
- EPA SmartWay for emissions methodology
- Open-source community for APIs and libraries

---

## 📞 Contact

For questions about this project or collaboration opportunities, reach out via:
- Email: mkpatel4102@gmail.com
- LinkedIn: [Your Profile]

**Built with 🌱 for a sustainable future in logistics**
