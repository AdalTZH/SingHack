# Decision Agent

The Decision Agent analyzes page sync data to determine if a user viewing a travel-related page might benefit from travel insurance. Instead of generating summaries, this agent acts as a decision maker that:

1. **Analyzes page content** to determine if it's travel-related
2. **Decides if insurance might be needed** based on the travel activity
3. **Generates catchy persuasion messages** (max 20 words) displayed in the cursor textbox when insurance should be offered

## Overview

When a user browses web pages with the extension enabled, page sync data is sent to the Decision Agent. The agent:

- Quickly filters non-travel pages using keyword matching
- Uses LLM analysis for nuanced decision-making on travel pages
- Generates catchy persuasion messages (max 20 words) for cursor textbox display
- Returns decision results with confidence scores and reasoning

## Features

- **Fast filtering**: Quick keyword-based pre-filtering to skip non-travel pages
- **LLM-powered decisions**: Uses OpenAI models for accurate travel-related and insurance need detection
- **Persuasion messages**: Generates catchy, short messages (max 20 words) displayed in cursor textbox
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

# Note: Master Agent forwarding has been removed - persuasion messages are now displayed directly in cursor textbox

# Decision Settings
DECISION_TEMPERATURE=0.3
DECISION_MAX_TOKENS=500
DECISION_CONFIDENCE_THRESHOLD=0.7
```

## Running the Server

### Quick Start

1. **Navigate to the decision_agent directory:**
```bash
cd Server/decision_agent
```

2. **Install dependencies (if not already installed):**
```bash
pip install -r requirements.txt
```

3. **Set your OpenAI API key:**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_api_key_here"

# Windows CMD
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

4. **Start the server:**
```bash
python -m decision_agent.server
```

Or using uvicorn directly:

```bash
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

### Server Output

When running successfully, you should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Initializing Decision Agent...
INFO:     Decision Agent initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8004
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
  "persuasion_message": "Protect your adventure! Travel insurance = peace of mind ✈️"
}
```

### `GET /health`

Health check endpoint.

## Integration

The Decision Agent is integrated with:

1. **Chrome Extension** (`background.js`): Sends page sync data to Decision Agent
2. **Cursor Textbox**: Displays persuasion messages when insurance should be offered

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
Generates Persuasion Message (max 20 words)
    ↓ (displays in cursor textbox)
User sees message with streaming animation (10 seconds)
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

## Persuasion Messages

The Decision Agent generates catchy, short persuasion messages (max 20 words) that are displayed in the cursor textbox when users visit travel-related pages. These messages:

- Are concise and won't take up screen space
- Are catchy and attention-grabbing
- Focus on the specific travel activity
- Create urgency or highlight value
- Display for 10 seconds with streaming animation

## Notes

- The Decision Agent does NOT generate summaries - it only makes decisions
- Page content is truncated to 10,000 characters for LLM analysis
- The agent generates persuasion messages (max 20 words) when `should_prompt` is True
- Messages are displayed in the cursor textbox with streaming animation
- Non-travel pages are filtered early to save API costs

