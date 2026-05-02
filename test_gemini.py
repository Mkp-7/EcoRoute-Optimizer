"""
Test Gemini API connection
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import and test
try:
    import google.generativeai as genai
    print("✓ google-generativeai library imported")
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GEMINI_API_KEY not found in environment")
        exit(1)
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    print("✓ Gemini configured")
    
    # List available models
    print("\n📋 Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Test a simple generation
    print("\n🧪 Testing model generation...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello in one word")
    print(f"✓ Response: {response.text}")
    
    print("\n✅ ALL TESTS PASSED!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
