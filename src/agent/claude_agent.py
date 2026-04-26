"""
Claude AI Agent for EcoRoute Optimizer
Handles natural language queries and generates route recommendations
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic")

from config.settings import ANTHROPIC_API_KEY
from src.routing.route_finder import route_finder
from src.routing.optimizer import optimizer
from src.agent.prompts import SYSTEM_PROMPT, TOOL_DESCRIPTIONS


class EcoRouteAgent:
    """AI Agent for intelligent route optimization"""
    
    def __init__(self, api_key: str = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
        
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key or self.api_key == "your_anthropic_key_here":
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"
        self.conversation_history = []
    
    def find_routes_tool(self, origin: str, destination: str, 
                        weight_lbs: float = 1000,
                        deadline_hours: Optional[float] = None) -> Dict:
        """Tool function: Generate route options"""
        routes = route_finder.generate_all_routes(
            origin=origin,
            destination=destination,
            weight_lbs=weight_lbs,
            deadline_hours=deadline_hours
        )
        
        return {
            "success": True,
            "routes": routes,
            "count": len(routes),
            "origin": origin,
            "destination": destination
        }
    
    def get_recommendation_tool(self, routes: List[Dict], 
                               preference: str = "balanced") -> Dict:
        """Tool function: Get route recommendation"""
        rec = optimizer.generate_recommendation(routes, preference)
        return rec
    
    def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute a tool and return results"""
        
        if tool_name == "find_routes":
            return self.find_routes_tool(**tool_input)
        
        elif tool_name == "get_recommendation":
            return self.get_recommendation_tool(**tool_input)
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def chat(self, user_message: str, stream: bool = False) -> str:
        """
        Send a message to Claude and get response
        
        Args:
            user_message: User's question/request
            stream: Whether to stream the response
        
        Returns:
            Claude's response text
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare tools
        tools = [
            TOOL_DESCRIPTIONS["find_routes"],
            TOOL_DESCRIPTIONS["get_recommendation"]
        ]
        
        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=self.conversation_history
        )
        
        # Process response
        assistant_message = {"role": "assistant", "content": response.content}
        final_text = ""
        
        # Handle tool calls
        while response.stop_reason == "tool_use":
            # Extract tool calls
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"\n[Tool Call: {tool_name}]")
                    print(f"Input: {json.dumps(tool_input, indent=2)}")
                    
                    # Execute tool
                    result = self.execute_tool(tool_name, tool_input)
                    
                    print(f"Result: {json.dumps(result, indent=2, default=str)[:200]}...")
                    
                    # Add tool result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str)
                    })
            
            # Add assistant message with tool calls
            self.conversation_history.append(assistant_message)
            
            # Add tool results
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation with tool results
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=self.conversation_history
            )
            
            assistant_message = {"role": "assistant", "content": response.content}
        
        # Extract final text response
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text
        
        # Add final assistant message to history
        
        self.conversation_history.append(assistant_message)
        
        return final_text
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


# Test function
def test_agent():
    """Test the AI agent with sample queries"""
    
    if not ANTHROPIC_AVAILABLE:
        print("Anthropic package not installed. Skipping test.")
        return
    
    print("\nTESTING CLAUDE AI AGENT\n")
    print("=" * 70)
    
    try:
        agent = EcoRouteAgent()
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\nPlease set your Anthropic API key in .env file:")
        print("ANTHROPIC_API_KEY=sk-ant-your-key-here\n")
        return
    
    # Test query
    print("\nUser Query:")
    print("-" * 70)
    query = "I need to ship 1500 lbs from San Francisco to Chicago. What are my options?"
    print(query)
    
    print("\n\nClaude's Response:")
    print("-" * 70)
    
    response = agent.chat(query)
    print(response)
    
    print("\n" + "=" * 70)
    print("AGENT TEST COMPLETE\n")


if __name__ == "__main__":
    test_agent()
