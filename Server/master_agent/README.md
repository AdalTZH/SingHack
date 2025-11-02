# Master Agent Server

Central orchestration agent that routes user queries to specialized agents and synthesizes responses.

## Overview

The Master Agent Server is a FastAPI application that acts as the central hub for the travel insurance AI system. It:

1. Receives queries from the Chrome extension
2. Routes queries to appropriate specialized agents (Classifier, Predict, Risk)
3. Synthesizes agent responses into coherent answers
4. Returns unified responses to the extension

## Architecture

### Agent Communication (A2A Protocol)

The Master Agent communicates with specialized agents via REST API:

```
Chrome Extension → Master Agent → Specialized Agents → Master Agent → Chrome Extension
                        ↓
                  LangGraph Orchestration
```

### Specialized Agents

| Agent | Purpose | Port |
|-------|---------|------|
| **Classifier Agent** | Classifies queries into types | 8001 |
| **Predict Agent** | Provides insurance recommendations | 8002 |
| **Risk Agent** | Assesses travel risks | 8003 |

## Installation

### 1. Install Dependencies

```bash
cd Server/master_agent
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the Server directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
MASTER_AGENT_HOST=0.0.0.0
MASTER_AGENT_PORT=9000
TEMPERATURE=0.7
```

### 3. Start the Server

```bash
python -m master_agent.server
```

Or using uvicorn directly:

```bash
uvicorn master_agent.server:app --host 0.0.0.0 --port 9000 --reload
```

## API Endpoints

### POST /chat

Main chat endpoint for processing user queries.

**Request:**
```json
{
  "message": "Which insurance plan is best for skiing in Japan?",
  "temperature": 0.7,
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on your skiing trip to Japan, I recommend...",
  "classification": "recommendation",
  "agents_consulted": ["predict", "risk"],
  "metadata": {
    "routing_decision": "predict"
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Master Agent API",
  "version": "1.0.0"
}
```

### GET /agents

List available specialized agents.

**Response:**
```json
{
  "agents": [
    {
      "name": "classifier",
      "description": "Classifies user queries into types",
      "capabilities": ["comparison", "explanation", "eligibility", "scenario"]
    },
    ...
  ],
  "total": 3
}
```

## Workflow

### 1. Query Routing

The Master Agent analyzes the user query and determines which agent(s) to consult:

- **Compare/Explain queries** → Classifier Agent
- **Recommendation queries** → Predict Agent
- **Risk assessment queries** → Risk Agent
- **General queries** → All agents as needed

### 2. Agent Orchestration

Using LangGraph, the Master Agent:
1. Routes the query to appropriate agents
2. Waits for responses
3. Synthesizes results

### 3. Response Synthesis

The Master Agent uses OpenAI to combine agent responses into:
- Clear, coherent answers
- Proper citations and reasoning
- User-friendly explanations

## Integration with Chrome Extension

The Chrome extension sends POST requests to `/chat`:

```javascript
const response = await fetch('http://localhost:9000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,
    temperature: 0.7
  })
});

const data = await response.json();
console.log(data.response); // Display to user
```

## Development

### Running Locally

```bash
# Start the server
python -m master_agent.server

# Server will be available at http://localhost:9000
```

### Testing

```bash
# Test health endpoint
curl http://localhost:9000/health

# Test chat endpoint
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which plan is best for Japan?"}'
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Configuration

Key configuration options in `config.py`:

- `SERVER_HOST`: Server bind address (default: 0.0.0.0)
- `SERVER_PORT`: Server port (default: 9000)
- `OPENAI_MODEL`: LLM model for synthesis (default: gpt-4o-mini)
- `TEMPERATURE`: Response creativity (default: 0.7)
- `AGENT_URLS`: Base URLs for specialized agents

## Architecture Diagram

```
┌─────────────────┐
│ Chrome Extension│
└────────┬────────┘
         │ HTTP POST /chat
         ↓
┌──────────────────────────────────┐
│      Master Agent (FastAPI)      │
│  ┌────────────────────────────┐  │
│  │   LangGraph Orchestration  │  │
│  │                            │  │
│  │  Route → Agents → Synthesize│  │
│  └────────────────────────────┘  │
└─────┬────────┬───────────┬───────┘
      │        │           │
      ↓        ↓           ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│Classifier│ │ Predict  │ │  Risk    │
│ :8001    │ │ :8002    │ │ :8003    │
└──────────┘ └──────────┘ └──────────┘
```

## Troubleshooting

### Server Won't Start

1. Check if port 9000 is available
2. Verify OpenAI API key is set
3. Ensure all dependencies are installed

### Agent Communication Errors

1. Verify specialized agents are running
2. Check agent URLs in configuration
3. Review network connectivity

### Poor Responses

1. Adjust temperature in configuration
2. Enable debug logging to see agent responses
3. Check LLM model availability and credits

## Future Enhancements

- [ ] Add caching for common queries
- [ ] Implement streaming responses
- [ ] Add user session management
- [ ] Support for multi-turn conversations
- [ ] Metrics and analytics
- [ ] Rate limiting and throttling

## License

Part of SingHack Travel Insurance System

