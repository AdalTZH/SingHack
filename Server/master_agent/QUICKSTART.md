# Master Agent Quick Start

Get the Master Agent running in 3 steps!

## ⚡ Quick Start

### 1️⃣ Install Dependencies

```bash
cd Server
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

Ensure `.env` file exists in `Server/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3️⃣ Start the Server

```bash
python -m master_agent.server
```

Server will start at `http://localhost:9000`

## 🧪 Test the API

### Using curl

```bash
# Health check
curl http://localhost:9000/health

# Send a chat message
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which insurance plan is best for traveling to Japan?"}'
```

### Using Python

```python
import requests

# Send a chat message
response = requests.post(
    'http://localhost:9000/chat',
    json={'message': 'Compare Product A and Product B'}
)

print(response.json())
```

## 🌐 Connect Chrome Extension

1. Update `Extension/config.js`:
```javascript
const CONFIG = {
    USE_MASTER_AGENT: true,
    MASTER_AGENT_URL: 'http://localhost:9000'
};
```

2. Reload the extension in Chrome
3. Open sidebar and start chatting!

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## 🤖 Agent Routing Logic

The Master Agent uses intelligent routing to call the appropriate specialized agent:

- **Insurance Plan Suggestions** → Goes directly to Predict Agent (no classification needed)
- **Risk Assessment Queries** → Goes directly to Risk Agent for weather, disaster, and activity risk analysis
- **Compare/Explain Queries** → Uses Classifier Agent to understand query intent, then provides response

**Example routing:**
- "Which insurance plan is best?" → Predict Agent
- "What are the risks of traveling to Japan?" → Risk Agent
- "Compare Product A and B" → Classifier Agent → Response

## 🌍 Complete System Setup

For full functionality, start all agents:

1. **Risk Agent** (port 8003) - Risk assessment
   ```bash
   python -m risk_agent.server
   ```

2. **Master Agent** (port 9000) - Orchestration
   ```bash
   python -m master_agent.server
   ```

## 🎯 Next Steps

- Read `README.md` for detailed architecture
- Explore agent integration examples
- Customize routing logic
- Add new specialized agents
- Test risk assessment with travel queries

## 🐛 Troubleshooting

**Server won't start?**
- Check if port 9000 is available
- Verify OpenAI API key is set
- Ensure all dependencies installed

**Extension can't connect?**
- Verify server is running: `curl http://localhost:9000/health`
- Check CORS settings in `config.py`
- Review extension console for errors

**Agent communication fails?**
- Verify specialized agents are accessible
- Check network connectivity
- Review master agent logs

