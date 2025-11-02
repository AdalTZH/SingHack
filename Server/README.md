# Singhacks - Travel Insurance Risk & Prediction System

A comprehensive travel insurance system with five AI agents that work together to assess travel risks, classify user queries, recommend suitable insurance plans, and analyze user browsing behavior.

## Overview

This project consists of five main components:

1. **Master Agent** - Central orchestration agent that routes queries to specialized agents
2. **Decision Agent** (NEW!) - Analyzes page sync data to determine if travel insurance should be offered
3. **Classifier Agent** - Classifies user queries into Comparison, Explanation, Eligibility, or Scenario Analysis
4. **Risk Agent** - Identifies potential travel risks (weather, natural disasters, advisories)
5. **Predict Agent** - Recommends insurance plans based on historical claims data

The Master Agent receives requests from a Chrome extension and coordinates with specialized agents via Agent-to-Agent (A2A) protocol. All agents also expose tools via MCP (Model Context Protocol) servers, making them accessible to AI assistants like Cursor.

## Project Structure

```
singhacks/
├── master_agent/          # Master Agent Package (Central Orchestration)
│   ├── server.py          # FastAPI server for Chrome extension
│   ├── master_agent.py    # Orchestration logic with LangGraph
│   ├── agent_client.py    # Agent-to-Agent (A2A) communication
│   ├── config.py          # Configuration (ports, URLs)
│   ├── requirements.txt   # Master agent dependencies
│   └── README.md          # Master Agent documentation
├── decision_agent/        # Decision Agent Package (Page Sync Analysis)
│   ├── server.py          # FastAPI server for page sync analysis
│   ├── decision_agent.py  # Decision-making logic with LLM
│   ├── api.py             # API interface
│   ├── config.py          # Configuration (ports, URLs)
│   ├── requirements.txt   # Decision agent dependencies
│   ├── README.md          # Decision Agent documentation
│   └── QUICKSTART.md      # Quick start guide
├── classifier_agent/      # Classifier Agent Package
│   ├── mcp_server.py      # MCP server with 3 query classification tools
│   ├── classifier_agent.py # Main classification logic with LangGraph
│   ├── api.py             # API interface
│   ├── taxonomy_loader.py # Taxonomy data loader
│   ├── config.py          # Configuration (model, taxonomy path)
│   ├── example_usage.py   # Usage examples
│   └── README.md          # Classifier Agent documentation
├── risk_agent/            # Risk Agent Package
│   ├── mcp_server.py      # MCP server with 6 risk assessment tools
│   ├── config.py          # Configuration (API keys, settings)
│   ├── example_usage.py   # Usage examples
│   ├── README.md          # Risk Agent documentation
│   └── SETUP.md           # Setup guide
├── predict_agent/         # Predict Agent Package
│   ├── mcp_server.py      # MCP server with 3 insurance recommendation tools
│   ├── predict_agent.py   # Main prediction logic
│   ├── api.py             # API interface
│   ├── database.py        # Database connection and queries
│   ├── config.py          # Configuration (database, scoring)
│   ├── user_data_model.py # User data model
│   ├── example_usage.py   # Usage examples
│   └── README.md          # Predict Agent documentation
├── requirements.txt       # Python dependencies
├── test_agents.py         # Test script for all agents
├── run_examples.py        # Run examples
├── Taxonomy_Hackathon.json # Insurance taxonomy data
├── Claims_Data_DB.pdf     # Database schema documentation
├── .env                   # Environment variables (API keys, DB credentials)
└── README.md              # This file
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root (or use existing one):

```env
# OpenAI API (for Classifier Agent)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini  # Optional

# Weather API (for Risk Agent)
OPENWEATHER_API_KEY=your_key_here

# Web Search API (for Risk Agent)
TAVILY_API_KEY=your_key_here

# Database (for Predict Agent)
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

### 3. Configure MCP Servers in Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "Tavily Expert": {
      "url": "https://gitmcp.io/tadata-org/fastapi_mcp"
    },
    "ClassifierAgentServer": {
      "command": "python",
      "args": ["-m", "classifier_agent.mcp_server"],
      "cwd": "C:\\Users\\YourPath\\SingHack-Backend\\Server"
    },
    "RiskAgentServer": {
      "command": "python",
      "args": ["-m", "risk_agent.mcp_server"],
      "cwd": "C:\\Users\\YourPath\\SingHack-Backend\\Server"
    },
    "PredictAgentServer": {
      "command": "python",
      "args": ["-m", "predict_agent.mcp_server"],
      "cwd": "C:\\Users\\YourPath\\SingHack-Backend\\Server"
    }
  }
}
```

**Note:** Update the `cwd` path to your actual project directory.

### 4. Install FastMCP

```bash
pip install fastmcp
```

### 5. Restart Cursor

After configuring MCP servers, restart Cursor to load them.

## Agents

### Decision Agent (NEW!)

Analyzes page sync data from Chrome extension to determine if travel insurance should be offered:

- **FastAPI Server**: Receives page sync data from Chrome extension
- **LLM-Powered Decisions**: Uses OpenAI models to analyze page content
- **Automatic Forwarding**: Forwards insurance prompts to Master Agent when appropriate

**Key Features:**
- Analyzes all page content via LLM to determine if travel-related
- Decides if insurance might be needed based on travel activity
- Automatically forwards insurance prompts to Master Agent
- Provides decision confidence scores and reasoning

**API Endpoints:**
- `POST /analyze` - Analyze page sync data and determine if insurance should be offered
- `GET /health` - Health check

**Documentation:** See `decision_agent/README.md` and `decision_agent/QUICKSTART.md`

### Master Agent

Central orchestration agent that routes queries and synthesizes responses:

- **FastAPI Server**: Receives requests from Chrome extension
- **LangGraph Orchestration**: Routes queries to specialized agents
- **Agent-to-Agent (A2A) Protocol**: Communicates with specialized agents via REST
- **Response Synthesis**: Combines agent responses into coherent answers

**Key Features:**
- Routes queries to appropriate agents (Classifier, Predict, Risk)
- Synthesizes multi-agent responses
- Provides unified API for Chrome extension
- Supports both direct agent communication and API calls

**API Endpoints:**
- `POST /chat` - Main chat endpoint for processing queries
- `GET /health` - Health check
- `GET /agents` - List available agents

**Documentation:** See `master_agent/README.md`

### Classifier Agent

Classifies user insurance queries using:
- LangGraph for workflow orchestration
- OpenAI GPT models for intelligent classification
- Taxonomy data loading and analysis

**Tools (3 total):**

1. `classify_insurance_query` - Classify a single query into one of four types
2. `get_classification_details` - Get detailed classification with next steps
3. `classify_batch_queries` - Classify multiple queries with summary statistics

**Documentation:** See `classifier_agent/README.md`

### Risk Agent

Identifies potential travel risks using:

- Weather forecasts (OpenWeatherMap)
- Natural disaster alerts (GDACS)
- Web search for travel risks (Tavily)
- Government travel advisories

**Tools (6 total):**

1. `get_weather_forecast` - Get weather forecast for location
2. `check_severe_weather` - Check for severe weather conditions
3. `check_natural_disasters` - Check natural disaster alerts
4. `web_search_risks` - Search web for travel risks
5. `comprehensive_risk_search` - Multi-category risk search
6. `check_travel_advisories` - Government travel advisories

**Documentation:** See `risk_agent/README.md`

### Predict Agent

Recommends insurance plans based on:

- Historical claims data analysis
- Destination-specific product performance
- User profile and coverage priorities
- Risk-adjusted scoring

**Tools (3 total):**

1. `find_insurance_plans` - Find suitable insurance plans
2. `get_product_statistics` - Get product performance statistics
3. `analyze_destination_coverage` - Analyze coverage for destination

**Documentation:** See `predict_agent/README.md`

## Usage

### Testing Agents

Test both agents:

```bash
python test_agents.py
```

### Running Examples

Run Predict Agent examples:

```bash
python run_examples.py
```

Or run individual agent examples:

```bash
python -m classifier_agent.example_usage
python -m predict_agent.example_usage
python -m risk_agent.example_usage
```

### Using via Chrome Extension

The system works with the Chrome extension:

1. **Start Required Servers**:
```bash
# Terminal 1: Master Agent (port 9000)
cd Server
python -m master_agent.server

# Terminal 2: Decision Agent (port 8004) - Required for page sync
cd Server
python -m decision_agent.server
```

2. **Configure Extension**:
   - Set `USE_MASTER_AGENT: true` in `Extension/config.js`
   - Ensure `DECISION_AGENT_URL` and `MASTER_AGENT_URL` are set
   - Extension will send chat requests to Master Agent and page sync to Decision Agent

3. **Use the System**:
   - **Chat**: Open the extension sidebar and ask questions about travel insurance
   - **Page Sync**: When enabled, Decision Agent automatically analyzes browsing and prompts for insurance when appropriate
   - Master Agent routes queries to appropriate specialized agents
   - Receive synthesized responses

### Using via MCP (Cursor AI Assistant)

Once MCP servers are configured, you can ask Cursor's AI assistant:

- **Query Classification**: "Classify this query: Which plan has better medical coverage?"
- **Risk Assessment**: "Check risks for traveling to Tokyo, Japan in March 2025"
- **Insurance Recommendations**: "Find insurance plans for a 35-year-old traveling to Japan for 10 days"

The AI will automatically call the appropriate tools from all agents.

## Integration

All four components work together:

1. **Master Agent** receives queries from Chrome extension and orchestrates workflow
2. **Classifier Agent** routes user queries to appropriate workflow
3. **Risk Agent** assesses travel risks
4. **Predict Agent** recommends insurance plans based on:
   - Identified risks
   - User profile
   - Historical claims data

### Example Workflow

**Chrome Extension Integration:**
```
Chrome Extension → Master Agent (FastAPI) → LangGraph Orchestration →
  ├─ Classifier Agent → Query Type Classification
  ├─ Predict Agent → Insurance Recommendations
  └─ Risk Agent → Risk Assessment
  → Master Agent Synthesizes → Chrome Extension
```

**MCP Integration:**
```
Cursor AI → MCP Servers → 
  ├─ Classifier Agent (MCP) → Query Type Classification
  ├─ Predict Agent (MCP) → Insurance Recommendations
  └─ Risk Agent (MCP) → Risk Assessment
  → Combined Results → Cursor AI
```

**Query Routing Examples:**
- Comparison Query → Compare products side-by-side
- Explanation Query → Provide detailed explanation with policy references
- Eligibility Query → Apply rule-based logic for yes/no answer
- Scenario Analysis → Model scenario step-by-step with benefits/exclusions

## Development

### Project Status

- ✅ Classifier Agent MCP Server - Functional
- ✅ Risk Agent MCP Server - Functional
- ✅ Predict Agent MCP Server - Functional
- ✅ Database Connection - Configured
- ✅ API Keys - Configured
- ✅ LangGraph & FastMCP - Installed

### Testing

```bash
# Test both agents
python test_agents.py

# Test individual components
python -m classifier_agent.example_usage
python -m predict_agent.example_usage
python -m risk_agent.example_usage
```

## Dependencies

Key dependencies:

- `langgraph` - Workflow orchestration for Classifier Agent
- `langchain-openai` - OpenAI integration
- `fastmcp` - MCP server framework
- `tavily-python` - Web search API
- `psycopg2-binary` - PostgreSQL database
- `pandas`, `numpy` - Data analysis
- `requests` - HTTP requests
- `python-dotenv` - Environment variables

See `requirements.txt` for complete list.

## Documentation

- **Classifier Agent**: `classifier_agent/README.md`
- **Risk Agent**: `risk_agent/README.md`
- **Predict Agent**: `predict_agent/README.md`
- **Database Schema**: `Claims_Data_DB.pdf`
- **Taxonomy**: `Taxonomy_Hackathon.json`

## Troubleshooting

### MCP Servers Not Starting

1. Verify FastMCP is installed: `pip install fastmcp langgraph langchain-openai`
2. Check Python path in `mcp.json`
3. Verify module imports: `python -c "import classifier_agent.mcp_server; import risk_agent.mcp_server; import predict_agent.mcp_server"`

### Database Connection Issues

1. Check database credentials in `.env` or `predict_agent/config.py`
2. Verify database is accessible from your network
3. Test connection: `python -c "from predict_agent.database import DatabaseConnection; db = DatabaseConnection(); print(db.connect())"`

### API Key Issues

1. Verify API keys in `.env` file
2. Check keys are loaded: `python test_agents.py`
3. Test API access directly

## License

[Add license information if applicable]
