# AI AGENT SETUP GUIDE

## WHAT WE JUST BUILT

You now have a complete AI-powered route optimization system!

Components:
1. **Claude AI Agent** - Natural language interface
2. **System Prompts** - Expert logistics assistant personality
3. **Tool Integration** - Agent can call route_finder and optimizer
4. **Interactive Demo** - Chat interface to test the system

---

## STEP 1: INSTALL ANTHROPIC SDK

```cmd
cd C:\Users\mkpat\OneDrive\Desktop\ecoroute-optimizer

# Activate virtual environment
venv\Scripts\activate

# Install Anthropic SDK
pip install anthropic
```

---

## STEP 2: ADD YOUR ANTHROPIC API KEY TO .env

Open `.env` file and replace:

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
```

With your actual key (starts with `sk-ant-api...`):

```bash
ANTHROPIC_API_KEY=sk-ant-api-your-actual-key-here
```

---

## STEP 3: TEST THE AI AGENT

### Option A: Test Script

```cmd
python src\agent\claude_agent.py
```

**Expected:**
```
TESTING CLAUDE AI AGENT
======================================================================

User Query:
----------------------------------------------------------------------
I need to ship 1500 lbs from San Francisco to Chicago. What are my options?

[Tool Call: find_routes]
Input: {
  "origin": "San Francisco",
  "destination": "Chicago",
  "weight_lbs": 1500
}

Claude's Response:
----------------------------------------------------------------------
I'll find the most efficient routes from San Francisco to Chicago...

Option 1: Intermodal (Truck + Rail) [RECOMMENDED]
- Cost: $1,556
- Time: 57 hours
- Carbon: 290 kg CO2

Option 2: Direct Diesel Truck
- Cost: $4,119
- Time: 43 hours  
- Carbon: 2,181 kg CO2

The intermodal route saves you $2,563 (62%) and reduces carbon by 1,891 kg (87%)...
```

### Option B: Interactive Demo

```cmd
python demo.py
```

**Then chat with the AI:**
```
You: I need to ship 1000 lbs from New York to LA

Agent: [Generates routes and recommendations]

You: What's the greenest option?

Agent: [Explains carbon-optimized route]

You: quit
```

---

## WHAT THE AI AGENT CAN DO

1. **Understand Natural Language**
   - "Ship 500 lbs to Chicago"
   - "What's the cheapest route?"
   - "I need it there by Friday"

2. **Generate Route Options**
   - Calls route_finder tool automatically
   - Shows 2-3 viable options
   - Includes diesel, electric, and intermodal

3. **Make Smart Recommendations**
   - Considers user preferences (cost/time/carbon)
   - Explains trade-offs clearly
   - Provides reasoning for recommendations

4. **Answer Follow-up Questions**
   - "Why is rail cheaper?"
   - "What if I need it faster?"
   - "How much carbon would I save?"

---

## EXAMPLE CONVERSATIONS

### Example 1: Cost-Focused
```
You: What's the cheapest way to ship 800 lbs from SF to Seattle?

Agent: I'll find the most cost-effective routes...

Intermodal (Truck + Rail): $245
- Cheapest option, saves $178 vs diesel
- Takes 18 hours (vs 12 hours)
- 78% lower carbon emissions

Diesel Truck: $423
- Fastest option
- Higher cost and carbon

For cost savings, I recommend intermodal.
```

### Example 2: Time-Sensitive
```
You: I need 1200 lbs in Chicago from LA by tomorrow afternoon

Agent: That's a tight deadline - about 30 hours...

Only diesel truck can meet this deadline:
- Cost: $2,856
- Time: 28 hours (arrives with 2hr buffer)
- Carbon: 1,823 kg CO2

Intermodal would take 52 hours and miss your deadline.
For urgent delivery, diesel is your only option.
```

### Example 3: Carbon-Focused
```
You: What's the greenest way to ship from Boston to Miami?

Agent: For the most environmentally friendly route...

Intermodal (Rail): 187 kg CO2
- 84% lower emissions than diesel
- Cost: $892 (actually cheaper!)
- Time: 42 hours

This is a great example where the greenest option
is also the most cost-effective.
```

---

## TROUBLESHOOTING

### "anthropic package not installed"
```cmd
pip install anthropic
```

### "API key not configured"
Add your key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api-your-key
```

### "Invalid API key"
Check that:
1. Key starts with `sk-ant-api...`
2. No extra spaces in .env
3. You copied the entire key

### Agent not calling tools
This is normal - Claude decides when to use tools.
Try more specific queries like:
- "Find routes from X to Y"
- "What are my shipping options?"

---

## PROJECT STATUS

```
COMPLETE:
- Route Finder (generates options)
- Carbon Calculator (emissions)
- Optimizer (rankings)
- AI Agent (natural language interface)

READY TO USE:
- Run demo.py for interactive chat
- Test with real shipping scenarios
- Show to potential employers/investors
```

---

## NEXT STEPS (OPTIONAL)

If you want to make it even better:

1. **Build Streamlit UI** (visual interface)
2. **Add more cities** (expand beyond 23 cities)
3. **Real-time pricing** (integrate actual carrier rates)
4. **Save quotes** (database persistence)
5. **PDF reports** (generate shipping quotes)

But what you have NOW is already:
- Production-quality code
- Real business value
- AI-powered intelligence
- Portfolio-ready

---

**Go ahead and test it! Let me know what the AI says!**
