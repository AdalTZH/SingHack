# Insights Agent

The Insights Agent determines whether to perform data analytics on user queries to provide insights that could help convince clients to purchase travel insurance.

## Overview

When a user sends a query, the Insights Agent:
1. Analyzes the query to determine if analytics would be valuable
2. If yes, calls the Insights Analytics system (duplicate of text2cypher) to perform data analysis
3. Returns persuasive insights based on real travel insurance claims data

## Architecture

```
User Query → Master Agent → Insights Agent → Insights Analytics (Neo4j) → Insights Text → Frontend
```

## Components

### 1. Insights Agent (`insights_agent.py`)
- Determines if analytics should be performed using GPT
- Calls the Insights Analytics API if needed
- Returns insights text for display

### 2. Insights Analytics (`insights_analytics.py`)
- Duplicate of `text2cypher.py` running on port 5001
- Converts natural language queries to Neo4j Cypher queries
- Executes queries and analyzes results
- Generates persuasive insights text

### 3. Integration
- Master Agent server calls Insights Agent for each user query
- Frontend displays insights in the InsightBubble component
- Insights replace hard-coded text dynamically

## Setup

### 1. Install Dependencies

```bash
cd Server/insights_agent
pip install -r requirements.txt
```

### 2. Start Insights Analytics Server

```bash
# From project root
python insights_analytics.py
# Runs on http://localhost:5001
```

### 3. Start Insights Agent Server

```bash
# From project root
python Server/start_insights_agent.py
# Runs on http://localhost:8008
```

Or:

```bash
cd Server/insights_agent
python -m insights_agent.server
```

### 4. Configure Environment Variables

Set in your environment or `.env` file:

```bash
OPENAI_API_KEY=your-api-key
INSIGHTS_ANALYTICS_URL=http://localhost:5001
INSIGHTS_AGENT_URL=http://localhost:8008  # For Master Agent
```

### 5. Start Master Agent

The Master Agent will automatically call the Insights Agent when processing queries.

```bash
python Server/start_master_agent.py
```

## API Endpoints

### Insights Agent (`http://localhost:8008`)

#### POST `/process`
Process a query and determine if analytics should be performed.

**Request:**
```json
{
  "query": "What are the risks of traveling to China?"
}
```

**Response:**
```json
{
  "should_analyze": true,
  "performed_analytics": true,
  "insights": "Flying to China isn't risk-free: there have already been 13,929 claims there...",
  "reasoning": "Query is about travel risks and would benefit from data analytics",
  "confidence": 0.95,
  "query_results": [...],
  "execution_time": "2.5s"
}
```

### Insights Analytics (`http://localhost:5001`)

#### POST `/query`
Process natural language query and return analytics insights.

**Request:**
```json
{
  "query": "What is the average claim amount for medical expenses in China?"
}
```

**Response:**
```json
{
  "user_query": "...",
  "cypher_queries": [...],
  "query_results": [...],
  "analysis": "Persuasive insights text...",
  "execution_time": "2.5s"
}
```

## How It Works

1. **User sends query** → Master Agent receives it
2. **Master Agent** → Calls Insights Agent `/process` endpoint
3. **Insights Agent** → Uses GPT to determine if analytics would be valuable
4. **If yes** → Calls Insights Analytics `/query` endpoint
5. **Insights Analytics** → Generates Cypher queries, executes on Neo4j, analyzes results
6. **Insights Agent** → Returns persuasive insights text
7. **Master Agent** → Includes insights in response
8. **Frontend** → Displays insights in InsightBubble component

## Frontend Integration

The frontend automatically displays insights when they're available:

- Insights are shown in the `InsightBubble` component
- Replaces hard-coded text dynamically
- Only shown when analytics are performed
- Located at `/html/body/div/div/div/div[1]/div[1]/div[2]/div[1]` in the DOM

## Example Queries That Trigger Analytics

- "What are the risks of traveling to China?"
- "How many claims happen in Thailand?"
- "What's the average medical expense claim?"
- "Which destinations have the most baggage loss?"
- "Should I get insurance for my trip to Japan?"

## Example Queries That Don't Trigger Analytics

- "Hello"
- "What is your company name?"
- "How do I contact support?"
- General small talk

## Troubleshooting

### Insights Agent not responding
- Check if server is running on port 8008
- Verify `INSIGHTS_AGENT_URL` environment variable

### Insights Analytics not responding
- Check if server is running on port 5001
- Verify Neo4j connection credentials
- Check OpenAI API key

### No insights displayed
- Check browser console for errors
- Verify Master Agent is calling Insights Agent
- Check if query triggered analytics (check Insights Agent logs)

## Files

- `insights_agent.py` - Main agent logic
- `api.py` - API wrapper
- `server.py` - Flask server
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `start_insights_agent.py` - Start script

## Notes

- The Insights Analytics system is a duplicate of `text2cypher.py` but runs on a different port (5001 vs 5000)
- The original `text2cypher.py` is not modified
- Insights are only generated when the agent determines analytics would be valuable
- The system gracefully handles failures (if Insights Agent is unavailable, chat still works)

