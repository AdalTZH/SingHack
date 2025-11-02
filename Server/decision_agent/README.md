# Decision Agent

The Decision Agent analyzes page sync data to determine if a user viewing a travel-related page might benefit from travel insurance. Instead of generating summaries, this agent acts as a decision maker that:

1. **Analyzes page content** to determine if it's travel-related
2. **Decides if insurance might be needed** based on the travel activity
3. **Automatically forwards prompts** to the Master Agent when insurance should be offered

## Overview

When a user browses web pages with the extension enabled, page sync data is sent to the Decision Agent. The agent:

- Quickly filters non-travel pages using keyword matching
- Uses LLM analysis for nuanced decision-making on travel pages
- Forwards insurance purchase prompts to the Master Agent when appropriate
- Returns decision results with confidence scores and reasoning

## Features

- **Fast filtering**: Quick keyword-based pre-filtering to skip non-travel pages
- **LLM-powered decisions**: Uses OpenAI models for accurate travel-related and insurance need detection
- **Automatic forwarding**: Seamlessly forwards insurance prompts to Master Agent
- **Confidence scoring**: Provides confidence scores for decision transparency
- **Non-intrusive**: Only prompts when confident insurance might be needed

## Installation

```bash
cd Server/decision_agent
pip install -r requirements.txt
```

## Configuration

Set environment variables in `.env` or your environment:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
DECISION_AGENT_HOST=0.0.0.0
DECISION_AGENT_PORT=8004

# Master Agent URL (for forwarding prompts)
MASTER_AGENT_URL=http://localhost:9000

# Decision Settings
DECISION_TEMPERATURE=0.3
DECISION_MAX_TOKENS=500
DECISION_CONFIDENCE_THRESHOLD=0.7
```

## Running the Server

```bash
python -m decision_agent.server
```

Or using uvicorn directly:

```bash
uvicorn decision_agent.server:app --host 0.0.0.0 --port 8004 --reload
```

## API Endpoints

### `POST /analyze`

Analyzes page sync data and determines if insurance should be offered.

**Request:**
```json
{
  "url": "https://example.com/flight-booking",
  "title": "Flight Booking - Example Airlines",
  "html_content": "Book your flight...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "should_prompt": true,
  "confidence": 0.85,
  "reasoning": "User is booking an international flight...",
  "is_travel_related": true,
  "insurance_needed": true,
  "travel_context": "international flight booking",
  "forwarded_to_master": true
}
```

### `GET /health`

Health check endpoint.

## Integration

The Decision Agent is integrated with:

1. **Chrome Extension** (`background.js`): Sends page sync data to Decision Agent
2. **Master Agent**: Receives insurance prompts forwarded by Decision Agent

## Decision Logic

The agent uses a two-stage approach:

1. **Quick Filter**: Keyword-based filtering to skip non-travel pages
2. **LLM Analysis**: Detailed analysis for travel-related pages using OpenAI models

Decision criteria:
- **Travel-related**: Contains travel keywords (flights, hotels, bookings, etc.)
- **Insurance needed**: Activity requires coverage (international travel, adventure activities, expensive trips)
- **Confidence threshold**: Only prompts if confidence exceeds threshold (default: 0.7)

## Architecture

```
Chrome Extension (background.js)
    ↓ (page sync data)
Decision Agent
    ↓ (if insurance needed)
Master Agent
    ↓ (insurance prompt)
User
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/

# Run with auto-reload
uvicorn decision_agent.server:app --reload
```

## Notes

- The Decision Agent does NOT generate summaries - it only makes decisions
- Page content is truncated to 5000 characters for LLM analysis
- The agent automatically forwards to Master Agent when `should_prompt` is True
- Non-travel pages are filtered early to save API costs

