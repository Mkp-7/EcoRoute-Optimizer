# 🌱 EcoRoute Optimizer

**AI-Powered Carbon-Optimized Logistics Platform**

> Find the most cost-effective and environmentally sustainable shipping routes between US cities using AI-powered optimization.

---

## 🎯 What It Does

EcoRoute Optimizer helps logistics companies reduce shipping costs by up to **62%** while cutting carbon emissions by up to **88%** through intelligent route optimization.

### Key Features

- 🤖 **AI-Powered Chat** - Natural language interface using Google Gemini
- 📊 **Multi-Objective Optimization** - Balances cost, time, and carbon emissions
- 🚂 **Intermodal Routing** - Truck + Rail combinations for long-distance efficiency
- 🌍 **Carbon Tracking** - EPA SmartWay methodology for accurate emissions
- 📍 **100+ US Cities** - Major metros, NYC area, and regional hubs
- ⚡ **Real-Time Analysis** - Instant route generation and recommendations

---

## 💡 Example Results

### San Francisco → Chicago (1,500 lbs)

| Route | Cost | Time | Carbon | Savings |
|-------|------|------|--------|---------|
| **Intermodal (Truck + Rail)** | $1,561 | 57 hrs | 292 kg CO2 | **62% cost, 88% carbon** |
| Diesel Truck | $4,113 | 43 hrs | 2,352 kg CO2 | Baseline |

**Environmental Impact:** Equivalent to **98 trees planted** or **448 gallons of gas saved**

---

## 🛠️ Technology Stack

- **AI:** Google Gemini (natural language processing)
- **Backend:** Python 3.11+
- **Frontend:** Streamlit web framework
- **APIs:** OpenRouteService, OpenWeatherMap
- **Data:** EPA SmartWay, EPA eGRID 2023
- **Database:** SQLite

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- API keys (all free):
  - [Google Gemini](https://aistudio.google.com/app/apikey)
  - [OpenWeather](https://openweathermap.org/api)
  - [OpenRouteService](https://openrouteservice.org/dev/#/signup)

### Setup

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/EcoRoute-Optimizer.git
cd EcoRoute-Optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Create .env file and add your keys:
# GEMINI_API_KEY=your-key-here
# OPENWEATHER_API_KEY=your-key-here
# OPENROUTE_SERVICE_API_KEY=your-key-here
```

---

## 🎮 Usage

### Web Interface (Recommended)

```bash
streamlit run app.py
```

Opens at: `http://localhost:8501`

**Two modes:**
1. **🤖 AI Chat** - "Ship 1000 lbs from NYC to LA"
2. **📊 Route Comparison** - Visual form with metrics

### Command Line

```bash
python demo.py
```

Interactive chat interface in terminal.

---

## 🌍 Supported Cities

**50+ Major US Cities including:**

- **NYC Metro:** Manhattan, Brooklyn, Queens, Bronx, Newark, Jersey City
- **California:** San Francisco, Los Angeles, San Diego, Oakland
- **Major Cities:** Chicago, Houston, Dallas, Boston, Seattle, Miami, Atlanta

---

## 📊 How It Works

1. **User Input** → Natural language query
2. **AI Processing** → Gemini extracts origin, destination, weight
3. **Route Generation** → Diesel truck, electric truck, intermodal (rail)
4. **Carbon Calculation** → EPA methodology with grid carbon intensity
5. **Optimization** → Multi-objective ranking
6. **Recommendation** → AI explains best option with reasoning

---

## 🎯 Business Value

### For Logistics Companies

- **Cost Reduction:** 50-62% savings on long-distance routes
- **ESG Compliance:** Scope 3 emissions reporting ready
- **Competitive Advantage:** First AI-powered carbon optimizer
- **Scalability:** Handles complex multi-modal routing

---

## 📝 License

MIT License - Free to use and modify

---

## 👤 Author

Built with ❤️ for sustainable logistics

---

## 📧 Contact

Questions or feedback? Open an issue on GitHub!

---

## 🌍 Supported Cities (Complete List)

### New York Metro Area (12 cities)
- Manhattan, Brooklyn, Queens, Bronx, Staten Island
- Newark, Jersey City, Hoboken, Paterson, Elizabeth, Clifton, Passaic

### California (5 cities)
- San Francisco, Los Angeles, San Diego, Sacramento, Oakland

### Texas (3 cities)
- Houston, Dallas, Austin

### Major US Cities (100+ more)
- **Northeast:** Boston, Philadelphia, Baltimore, Pittsburgh, Cleveland, Cincinnati
- **Southeast:** Atlanta, Miami, Orlando, Tampa, Charlotte, Nashville, Raleigh, Jacksonville
- **Midwest:** Chicago, Detroit, Milwaukee, Minneapolis, Indianapolis, Columbus, St Louis, Kansas City, Memphis
- **West:** Seattle, Portland, Denver, Phoenix, Las Vegas

**Total: 50+ cities across the United States**

Need a city not listed? Open an issue on GitHub!
