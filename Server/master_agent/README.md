# Master Agent - Insurance Agent

A conversational insurance agent powered by LangGraph and GPT models. This agent provides expert insurance advice through a chat interface.

## Features

- **LangGraph-based workflow**: Uses LangGraph for state management and conversation flow
- **GPT-powered**: Leverages OpenAI GPT models for natural language understanding and generation
- **Insurance expertise**: Specialized in travel insurance, health insurance, and general insurance products
- **Conversation history**: Supports multi-turn conversations with context retention
- **RESTful API**: FastAPI-based server with `/chat` endpoint

## Architecture

The master agent is built using:
- **LangGraph**: For workflow orchestration and state management
- **LangChain**: For LLM integration
- **FastAPI**: For HTTP API server
- **OpenAI GPT**: For language model capabilities

## Installation

1. Install dependencies:
```bash
cd Server/master_agent
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file in Server directory):
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
MASTER_AGENT_HOST=0.0.0.0
MASTER_AGENT_PORT=9000
MASTER_AGENT_TEMPERATURE=0.7
MASTER_AGENT_MAX_TOKENS=2000
```

## Running the Server

From the `Server` directory:
```bash
python start_master_agent.py
```

Or directly:
```bash
cd Server/master_agent
python -m uvicorn master_agent.server:app --host 0.0.0.0 --port 9000 --reload
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Chat
```bash
POST /chat
Content-Type: application/json

{
    "message": "What does travel insurance cover?",
    "temperature": 0.7,
    "conversation_history": []
}
```

**Response:**
```json
{
    "success": true,
    "response": "Travel insurance typically covers...",
    "conversation_history": [
        {
            "user": "What does travel insurance cover?",
            "assistant": "Travel insurance typically covers..."
        }
    ],
    "metadata": {
        "model": "gpt-4o",
        "iterations": 1
    }
}
```

## Integration with Extension

The master agent is designed to work with the browser extension's chat interface. The extension sends requests to:
- `http://localhost:9000/chat` (or configured `MASTER_AGENT_URL`)

## Configuration

Key configuration options in `config.py`:
- `OPENAI_MODEL`: GPT model to use (default: `gpt-4o`)
- `TEMPERATURE`: Response creativity (default: `0.7`)
- `MAX_TOKENS`: Maximum response length (default: `2000`)
- `MAX_ITERATIONS`: Maximum workflow iterations (default: `15`)

## LangGraph Workflow

The agent uses a LangGraph workflow with:
1. **Agent Node**: Processes messages and generates responses
2. **Check Iterations Node**: Monitors iteration count
3. **Conditional Edges**: Determines when to continue or end conversation

## System Prompt

The agent is configured with a specialized insurance agent system prompt that:
- Establishes professional insurance expertise
- Defines key areas of coverage
- Sets tone and behavior expectations

## Error Handling

The agent includes comprehensive error handling:
- LLM invocation errors
- State management errors
- API request/response errors

## Development

To modify the agent behavior:
1. Update `INSURANCE_AGENT_SYSTEM_PROMPT` in `config.py`
2. Modify workflow nodes in `master_agent.py`
3. Adjust temperature and model settings

## Testing

Test the API using curl:
```bash
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is travel insurance?"}'
```

Or use the FastAPI docs at `http://localhost:9000/docs`
