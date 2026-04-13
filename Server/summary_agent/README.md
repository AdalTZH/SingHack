# Summary Agent

The Summary Agent extracts key information from travel-related page content to provide context for the Master Agent. When a user browses travel pages, the Summary Agent creates concise summaries that are stored in the Master Agent's state, enabling personalized insurance recommendations based on browsing history.

## Overview

**Process Flow:**
1. Decision Agent determines page is travel-related (`should_prompt=true`)
2. Extension sends page content to Summary Agent
3. Summary Agent extracts key information (destinations, dates, booking details, activities)
4. Summary is stored in Master Agent state as `page_summaries`
5. Master Agent uses accumulated summaries to provide contextual insurance advice

## Features

- **Key Information Extraction**: Captures travel type, destinations, dates, booking details
- **Concise Summaries**: Maximum 200 words, focused on insurance-relevant details
- **Accumulative Context**: Multiple page summaries stored for comprehensive user profile
- **LLM-Powered**: Uses OpenAI models for intelligent extraction

## Installation

```bash
cd Server/summary_agent
pip install -r requirements.txt
```

## Configuration

Set environment variables in `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
SUMMARY_AGENT_HOST=0.0.0.0
SUMMARY_AGENT_PORT=8020

# Summary Settings
SUMMARY_TEMPERATURE=0.3
SUMMARY_MAX_TOKENS=300
```

## Running the Server

### Quick Start

```bash
# Navigate to the summary_agent directory
cd Server/summary_agent

# Start the server
python -m summary_agent.server
```

Or using uvicorn directly:

```bash
uvicorn summary_agent.server:app --host 0.0.0.0 --port 8020 --reload
```

### Verify Server is Running

Visit: `http://localhost:8020/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "Summary Agent API",
  "version": "1.0.0"
}
```

## API Endpoints

### `POST /summarize`

Summarizes travel-related page content.

**Request:**
```json
{
  "inner_text": "Flight booking page content...",
  "url": "https://example.com/flight-booking",
  "title": "Flight Booking - Example Airlines",
  "travel_context": "international flight booking"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "**Travel Type**: International Flight\n**Destination**: Tokyo, Japan\n**Dates**: Dec 15-22, 2024\n**Key Details**:\n- Flight: SQ123 (Singapore to Tokyo)\n- Price: $850\n- 2 passengers\n- Return flight included",
  "url": "https://example.com/flight-booking",
  "title": "Flight Booking - Example Airlines",
  "travel_context": "international flight booking",
  "metadata": {
    "model": "gpt-4o-mini",
    "summary_length": 185,
    "content_length": 5230
  }
}
```

### `GET /health`

Health check endpoint.

## Integration Flow

```
Extension (content.js)
    ↓
Decision Agent
    ↓ (if should_prompt=true)
Extension receives decision + inner_text
    ↓
Summary Agent (POST /summarize)
    ↓
Extension stores summary
    ↓ (when user opens chatbot)
Master Agent receives page_summaries in state
    ↓
Master Agent uses summaries for contextual responses
```

## Summary Format

The Summary Agent extracts:

1. **Travel Type**: Flight, hotel, tour, activity, etc.
2. **Destination**: Countries, cities, locations
3. **Dates**: Travel dates, booking dates
4. **Booking Details**: Flight numbers, hotel names, prices, confirmation numbers
5. **Activities**: Planned activities (adventure sports, excursions)
6. **Important Details**: Group size, special requirements, cancellation policies

## Master Agent Integration

Summaries are stored in Master Agent's `AgentState.page_summaries` field:

```python
page_summaries: Optional[List[Dict[str, Any]]]
```

Each summary contains:
- `summary`: Extracted key information (str)
- `url`: Page URL (str)
- `title`: Page title (str)
- `travel_context`: Travel type (str)
- `metadata`: Summary metadata (dict)

## Example Usage

**Python:**
```python
from summary_agent import SummaryAgentAPI

api = SummaryAgentAPI()
result = api.summarize_page(
    inner_text="Flight booking content...",
    url="https://example.com/flights",
    title="Book Flights",
    travel_context="international flight"
)
print(result['summary'])
```

**HTTP:**
```bash
curl -X POST http://localhost:8020/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "inner_text": "Flight booking content...",
    "url": "https://example.com/flights",
    "title": "Book Flights",
    "travel_context": "international flight"
  }'
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn summary_agent.server:app --reload --port 8020
```

## Notes

- Summaries are designed to be concise (max 200 words) but complete
- Focus on information relevant to insurance recommendations
- Summaries accumulate in Master Agent state for comprehensive context
- Works seamlessly with Decision Agent and Master Agent

