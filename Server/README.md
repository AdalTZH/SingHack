# Singhacks - Travel Insurance Decision System

A travel insurance decision system that analyzes user browsing behavior to determine when travel insurance should be offered.

## Overview

This project consists of the **Decision Agent**, which analyzes page sync data from a Chrome extension to determine if a user viewing a travel-related page might benefit from travel insurance.

## Project Structure

```
Server/
├── decision_agent/        # Decision Agent Package (Page Sync Analysis)
│   ├── server.py          # FastAPI server for page sync analysis
│   ├── decision_agent.py  # Decision-making logic with LLM
│   ├── api.py             # API interface
│   ├── config.py          # Configuration (ports, URLs)
│   ├── requirements.txt   # Decision agent dependencies
│   ├── README.md          # Decision Agent documentation
│   └── QUICKSTART.md      # Quick start guide
├── requirements.txt       # Python dependencies
├── start_decision_agent.py # Script to start the decision agent server
├── Taxonomy_Hackathon.json # Insurance taxonomy data
├── Claims_Data_DB.pdf     # Database schema documentation
├── .env                   # Environment variables (API keys)
└── README.md              # This file
```

## Installation

### 1. Install Dependencies

```bash
cd Server
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the Server directory (or use existing one):

```env
# OpenAI API (for Decision Agent)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini  # Optional

# Server Configuration
DECISION_AGENT_HOST=0.0.0.0
DECISION_AGENT_PORT=8004

# Decision Settings
DECISION_TEMPERATURE=0.3
DECISION_MAX_TOKENS=500
DECISION_CONFIDENCE_THRESHOLD=0.7
```

## Decision Agent

Analyzes page sync data from Chrome extension to determine if travel insurance should be offered:

- **FastAPI Server**: Receives page sync data from Chrome extension
- **LLM-Powered Decisions**: Uses OpenAI models to analyze page content
- **Persuasion Messages**: Generates catchy, short messages (max 20 words) displayed in cursor textbox

**Key Features:**
- Analyzes all page content via LLM to determine if travel-related
- Decides if insurance might be needed based on travel activity
- Generates persuasion messages (max 20 words) for cursor textbox display
- Provides decision confidence scores and reasoning
- Non-intrusive: Only prompts when confident insurance might be needed

**API Endpoints:**
- `POST /analyze` - Analyze page sync data and determine if insurance should be offered
- `GET /health` - Health check

**Documentation:** See `decision_agent/README.md` and `decision_agent/QUICKSTART.md`

## Usage

### Starting the Server

**Option 1: Using the start script**
```bash
cd Server
python start_decision_agent.py
```

**Option 2: Using uvicorn directly**
```bash
cd Server
python -m decision_agent.server
```

Or:
```bash
cd Server
uvicorn decision_agent.server:app --host 0.0.0.0 --port 8004 --reload
```

### Verify Server is Running

Open your browser and visit:
```
http://localhost:8004/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "Decision Agent API",
  "version": "1.0.0"
}
```

### Using via Chrome Extension

The system works with the Chrome extension:

1. **Start Decision Agent Server**:
```bash
cd Server
python -m decision_agent.server
```

2. **Configure Extension**:
   - Ensure `DECISION_AGENT_URL` is set in `Extension/config.js`
   - Extension will send page sync data to Decision Agent

3. **Use the System**:
   - **Page Sync**: When enabled, Decision Agent automatically analyzes browsing and prompts for insurance when appropriate
   - Persuasion messages are displayed in the cursor textbox with streaming animation (10 seconds)

## Architecture

```
Chrome Extension (background.js)
    ↓ (page sync data)
Decision Agent
    ↓ (if insurance needed)
Generates Persuasion Message (max 20 words)
    ↓ (displays in cursor textbox)
User sees message with streaming animation (10 seconds)
```

## Decision Logic

The agent uses a two-stage approach:

1. **Quick Filter**: Keyword-based filtering to skip non-travel pages
2. **LLM Analysis**: Detailed analysis for travel-related pages using OpenAI models

Decision criteria:
- **Travel-related**: Contains travel keywords (flights, hotels, bookings, etc.)
- **Insurance needed**: Activity requires coverage (international travel, adventure activities, expensive trips)
- **Confidence threshold**: Only prompts if confidence exceeds threshold (default: 0.7)

## Development

### Project Status

- ✅ Decision Agent - Functional
- ✅ FastAPI Server - Running on port 8004
- ✅ LLM Integration - OpenAI models configured

### Testing

Test the Decision Agent:

```bash
# Health check
curl http://localhost:8004/health

# Test analysis endpoint
curl -X POST http://localhost:8004/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/flight-booking",
    "title": "Flight Booking - Example Airlines",
    "html_content": "Book your flight..."
  }'
```

## Dependencies

Key dependencies:

- `fastapi` - FastAPI web framework
- `uvicorn` - ASGI server
- `langchain-openai` - OpenAI integration
- `python-dotenv` - Environment variables
- `pydantic` - Data validation

See `requirements.txt` for complete list.

## Documentation

- **Decision Agent**: `decision_agent/README.md`
- **Quick Start**: `decision_agent/QUICKSTART.md`
- **Database Schema**: `Claims_Data_DB.pdf`
- **Taxonomy**: `Taxonomy_Hackathon.json`

## Troubleshooting

### Server Not Starting

1. Verify OpenAI API key is set in `.env` file
2. Check port 8004 is not already in use
3. Verify dependencies are installed: `pip install -r requirements.txt`

### API Key Issues

1. Verify API key in `.env` file
2. Check key is loaded: `python -c "from decision_agent.config import OPENAI_API_KEY; print('Key set' if OPENAI_API_KEY else 'Key missing')"`
3. Test API access directly

### Decision Agent Not Responding

1. Check server logs for errors
2. Verify OpenAI API key is valid
3. Test health endpoint: `curl http://localhost:8004/health`

## License

[Add license information if applicable]
