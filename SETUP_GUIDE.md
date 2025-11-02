# SingHack Backend - Complete Setup Guide

Complete guide to set up and run the multi-agent travel insurance system.

## 🎯 System Architecture

```
Chrome Extension
      ↓
Master Agent (FastAPI Server on :9000)
      ↓
┌─────┴─────┬───────┬────────┐
│           │       │        │
Classifier  Predict  Risk   (Future agents)
Agent       Agent   Agent
:8001       :8002   :8003
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- PostgreSQL database (for Predict Agent)
- Chrome browser (for extension)

## 🚀 Setup Steps

### 1. Install Dependencies

```bash
cd Server
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (for Master Agent server)
- LangGraph (for orchestration)
- LangChain OpenAI (for LLM integration)
- FastMCP (for MCP servers)
- All specialized agent dependencies

### 2. Configure Environment

Create/update `.env` file in `Server/`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Master Agent Configuration
MASTER_AGENT_HOST=0.0.0.0
MASTER_AGENT_PORT=9000

# Database Configuration (for Predict Agent)
DB_HOST=hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=hackathon_db
DB_USER=hackathon_user
DB_PASSWORD=Hackathon2025!

# API Keys (for Risk Agent)
OPENWEATHER_API_KEY=your_openweather_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### 3. Start Master Agent Server

```bash
cd Server
python -m master_agent.server
```

Server starts at: `http://localhost:9000`

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

### 4. Configure Chrome Extension

Edit `Extension/config.js`:

```javascript
const CONFIG = {
    OPENAI_API_KEY: 'your_api_key',
    MASTER_AGENT_URL: 'http://localhost:9000',
    USE_MASTER_AGENT: true  // Enable master agent mode
};
```

### 5. Load Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select the `Extension` folder
5. Extension is ready!

## 🧪 Test the System

### Test Master Agent Directly

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which insurance plan is best for skiing in Japan?"}'
```

### Test Chrome Extension

1. Click the extension icon in Chrome
2. Sidebar opens with chat interface
3. Type: "Compare Product A and Product B for medical coverage"
4. Wait for response from Master Agent

## 🔄 How It Works

### Message Flow

1. **User sends message** in Chrome extension sidebar
2. **Extension calls** `POST http://localhost:8000/chat` with message
3. **Master Agent receives** query and analyzes it
4. **LangGraph orchestrates** routing decision:
   - If comparison/explanation → Classifier Agent
   - If recommendation → Predict Agent
   - If risk assessment → Risk Agent
5. **Specialized agents** process and return results
6. **Master Agent synthesizes** responses using OpenAI
7. **Final response** sent back to extension
8. **User sees** comprehensive answer

### Agent Coordination

The Master Agent uses **Agent-to-Agent (A2A) protocol** via REST:
- Each agent can run as standalone service
- HTTP endpoints for inter-agent communication
- Fallback mechanisms if agents unavailable

## 📊 API Endpoints

### Master Agent API (Port 9000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/chat` | POST | Main chat endpoint |
| `/agents` | GET | List available agents |

### Swagger Documentation

Once server is running:
- **Swagger UI**: `http://localhost:9000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Development

### Running Individual Agents

```bash
# Test Classifier Agent
python -m classifier_agent.example_usage

# Test Predict Agent
python -m predict_agent.example_usage

# Test Risk Agent
python -m risk_agent.example_usage

# Run all tests
python test_agents.py
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then restart the server.

## 🐛 Troubleshooting

### Server won't start

**Problem**: Port 9000 already in use
```bash
# Find process using port
netstat -ano | findstr :9000  # Windows
lsof -i :9000                 # Mac/Linux

# Kill process or change port in config
```

### Extension can't connect

**Problem**: CORS errors
- Check `ALLOWED_ORIGINS` in `Server/master_agent/config.py`
- Verify extension URL matches allowed origins

**Problem**: Connection refused
- Verify server is running: `curl http://localhost:9000/health`
- Check firewall settings

### Agent communication fails

**Problem**: Import errors
- Verify all agents are in `Server/` directory
- Check Python path includes `Server/`

**Problem**: API calls timeout
- Check network connectivity
- Verify specialized agents are running
- Review logs for specific errors

## 📁 Directory Structure

```
SingHack-Backend/
├── Server/
│   ├── master_agent/          # NEW! Central orchestration
│   │   ├── server.py          # FastAPI server
│   │   ├── master_agent.py    # Orchestration logic
│   │   ├── agent_client.py    # A2A communication
│   │   ├── config.py
│   │   └── README.md
│   ├── classifier_agent/      # Query classification
│   ├── predict_agent/         # Recommendations
│   ├── risk_agent/           # Risk assessment
│   ├── requirements.txt
│   └── README.md
├── Extension/
│   ├── background.js          # UPDATED! Calls master agent
│   ├── config.js              # Configuration
│   ├── sidepanel.html/js      # UI
│   └── README.md
├── Payments/                  # Payment integration
└── README.md                  # Main documentation
```

## 🎓 Next Steps

1. **Customize routing**: Modify `_route_query()` in `master_agent.py`
2. **Add new agents**: Extend the orchestration graph
3. **Improve synthesis**: Tune prompts in `_synthesize_response()`
4. **Add caching**: Implement response caching for common queries
5. **Add monitoring**: Add metrics and logging

## 📚 Documentation

- **Master Agent**: `Server/master_agent/README.md`
- **Classifier Agent**: `Server/classifier_agent/README.md`
- **Predict Agent**: `Server/predict_agent/README.md`
- **Risk Agent**: `Server/risk_agent/README.md`
- **Extension**: `Extension/README.md`
- **Main README**: `README.md`

## ✅ Verification Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Master Agent server starts successfully
- [ ] Health check returns 200 OK
- [ ] Chrome extension loads without errors
- [ ] Extension can send and receive messages
- [ ] Master Agent routes to correct agents
- [ ] Responses are synthesized correctly
- [ ] Error handling works gracefully

## 🎉 Success!

If all checkboxes are green, your multi-agent system is fully operational!

The system now:
- ✅ Receives messages from Chrome extension
- ✅ Routes queries intelligently
- ✅ Coordinates multiple specialized agents
- ✅ Synthesizes comprehensive responses
- ✅ Returns user-friendly answers

## 🔗 Related Files

- Master Agent setup: `Server/master_agent/QUICKSTART.md`
- API reference: `Server/master_agent/README.md`
- Extension guide: `Extension/README.md`
- Main documentation: `README.md`

---

**Happy coding! 🚀**

