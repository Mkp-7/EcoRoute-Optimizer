"""
API Key Testing Script
Test each API key individually to make sure it works
"""

import requests

print("\n🔑 API KEY TESTING SCRIPT\n")
print("=" * 60)

# =============================================================================
# TEST 1: ANTHROPIC CLAUDE API
# =============================================================================
print("\n1️⃣  TESTING ANTHROPIC CLAUDE API")
print("-" * 60)

ANTHROPIC_KEY = input("Enter your Anthropic API key (sk-ant-...): ").strip()

if ANTHROPIC_KEY:
    try:
        # Simple test with requests (no SDK needed)
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Say hello!"}]
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Anthropic API is working!")
            data = response.json()
            print(f"   Response: {data['content'][0]['text']}")
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  Skipped (no key provided)")

# =============================================================================
# TEST 2: OPENWEATHER API
# =============================================================================
print("\n2️⃣  TESTING OPENWEATHER API")
print("-" * 60)

OPENWEATHER_KEY = input("Enter your OpenWeather API key: ").strip()

if OPENWEATHER_KEY:
    try:
        # Test with San Francisco coordinates
        lat, lon = 37.7749, -122.4194
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS! OpenWeather API is working!")
            data = response.json()
            print(f"   Location: {data['name']}")
            print(f"   Temperature: {data['main']['temp']}°C")
            print(f"   Wind Speed: {data['wind']['speed']} m/s")
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  Skipped (no key provided)")

# =============================================================================
# TEST 3: OPENROUTESERVICE API
# =============================================================================
print("\n3️⃣  TESTING OPENROUTESERVICE API")
print("-" * 60)

OPENROUTE_KEY = input("Enter your OpenRouteService API key: ").strip()

if OPENROUTE_KEY:
    try:
        # Test route from SF to LA
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {
            "Authorization": OPENROUTE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "coordinates": [
                [-122.4194, 37.7749],  # San Francisco (lon, lat)
                [-118.2437, 34.0522]   # Los Angeles (lon, lat)
            ],
            "units": "km"
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("✅ SUCCESS! OpenRouteService API is working!")
            data = response.json()
            route = data['routes'][0]
            summary = route['summary']
            print(f"   Distance: {summary['distance']:.1f} km")
            print(f"   Duration: {summary['duration']/3600:.1f} hours")
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  Skipped (no key provided)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("📊 TESTING COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("1. Save working API keys to your .env file")
print("2. For any failed tests, double-check the API key")
print("3. We can build the project with just Anthropic + OpenWeather!")
print("\n")
