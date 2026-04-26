"""
EcoRoute Optimizer - Interactive Demo
Chat with the AI agent to get route recommendations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent.gemini_agent import GeminiRouteAgent, GEMINI_AVAILABLE

def print_header():
    """Print demo header"""
    print("\n" + "=" * 70)
    print("ECOROUTE OPTIMIZER - AI ROUTE ASSISTANT (Powered by Google Gemini)")
    print("=" * 70)
    print("\nI help you find the most cost-effective and carbon-efficient")
    print("shipping routes between US cities.")
    print("\nExample queries:")
    print("  - 'Ship 1000 lbs from New York to Los Angeles'")
    print("  - 'What's the cheapest way to get 500 lbs to Chicago?'")
    print("  - 'I need the greenest route from SF to Seattle'")
    print("\nType 'quit' to exit\n")
    print("=" * 70)


def main():
    """Run interactive demo"""
    
    if not GEMINI_AVAILABLE:
        print("\nERROR: google-generativeai package not installed")
        print("Install it with: pip install google-generativeai\n")
        return
    
    print_header()
    
    # Initialize agent
    try:
        agent = GeminiRouteAgent()
        print("\nGemini AI Agent initialized! Ready to help.\n")
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\nPlease add your Gemini API key to .env:")
        print("GEMINI_API_KEY=AIza-your-key-here")
        print("\nGet a free key at: https://aistudio.google.com/app/apikey\n")
        return
    except Exception as e:
        print(f"\nERROR initializing agent: {e}\n")
        return
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for quit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye! Thanks for using EcoRoute Optimizer.\n")
                break
            
            # Get response from agent
            print("\nAgent: ", end="", flush=True)
            response = agent.chat_message(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
