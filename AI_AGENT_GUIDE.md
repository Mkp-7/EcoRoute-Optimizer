# AI Agent Guide - EcoRoute Optimizer

## Overview

The AI agent uses **Google Gemini** to understand natural language queries and generate intelligent route recommendations.

## How It Works

1. **User asks:** "Ship 1000 lbs from NYC to LA"
2. **Agent extracts:**
   - Origin: New York
   - Destination: Los Angeles
   - Weight: 1000 lbs
3. **Generates routes:** Diesel, Electric (if < 400km), Intermodal
4. **Calculates:** Cost, time, carbon for each option
5. **Recommends:** Best option with detailed reasoning

## API Key Setup

Get a free Gemini API key: https://aistudio.google.com/app/apikey

Add to `.env`:
```bash
GEMINI_API_KEY=AIza-your-key-here
```

## Usage

### In Streamlit (Web UI)
```bash
streamlit run app.py
```
Select "AI Chat Assistant" mode and start chatting!

### In CLI
```bash
python demo.py
```

## Example Queries

```
"Ship 1500 lbs from San Francisco to Chicago"
"What's the cheapest way to send 2000 lbs to Miami?"
"I need the greenest route from New York to Seattle"
"Ship from Queens to Chicago by Friday"
```

## Features

- ✅ Natural language understanding
- ✅ Automatic tool calling (route generation)
- ✅ Context-aware responses
- ✅ Savings calculations
- ✅ Environmental impact metrics
- ✅ Follow-up questions

## Technical Details

**Model:** `gemini-1.5-flash` (free tier)
**Rate Limits:** 60 requests/min, 1,500/day (free)
**Package:** `google-genai` (v1.0+)

## Troubleshooting

**"Package not installed"**
```bash
pip install google-genai
```

**"API key not configured"**
Check your `.env` file has `GEMINI_API_KEY`

**"Model not found"**
Make sure using `gemini-1.5-flash` (not experimental models)

## Code Location

- **Agent:** `src/agent/gemini_agent.py`
- **Prompts:** `src/agent/prompts.py`
- **Demo:** `demo.py`
- **Web UI:** `app.py`
