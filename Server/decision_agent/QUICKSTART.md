# Decision Agent Quick Start

Get the Decision Agent running in 3 steps!

## ⚡ Quick Start

### 1️⃣ Install Dependencies

```bash
cd Server/decision_agent
pip install -r requirements.txt
```

Or from the Server directory:
```bash
cd Server
pip install -r decision_agent/requirements.txt
```

### 2️⃣ Configure Environment

Ensure `.env` file exists in `Server/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Decision Agent Configuration (optional)
DECISION_AGENT_HOST=0.0.0.0
DECISION_AGENT_PORT=8004
MASTER_AGENT_URL=http://localhost:9000
DECISION_TEMPERATURE=0.3
DECISION_MAX_TOKENS=500
DECISION_CONFIDENCE_THRESHOLD=0.7
```

### 3️⃣ Start the Server

**Option 1: Using the startup script (Recommended)**
```bash
cd Server
python start_decision_agent.py
```

**Option 2: Using Python module**
```bash
cd Server
python -m decision_agent.server
```

**Option 3: Using uvicorn directly**
```bash
cd Server
uvicorn decision_agent.server:app --host 0.0.0.0 --port 8004 --reload
```

Server will start at `http://localhost:8004`

## 🧪 Test the API

### Using curl

```bash
# Health check
curl http://localhost:8004/health

# Analyze a page
curl -X POST http://localhost:8004/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/flight-booking",
    "title": "Flight Booking - Example Airlines",
    "html_content": "Book your flight to Tokyo..."
  }'
```

### Using Python

```python
import requests

# Analyze a page
response = requests.post(
    'http://localhost:8004/analyze',
    json={
        'url': 'https://example.com/flight-booking',
        'title': 'Flight Booking',
        'html_content': 'Book your flight...'
    }
)

print(response.json())
```

## 🌐 Connect Chrome Extension

1. Ensure `Extension/config.js` has the Decision Agent URL:
```javascript
const CONFIG = {
    DECISION_AGENT_URL: 'http://localhost:8004',
    MASTER_AGENT_URL: 'http://localhost:9000'
};
```

2. Make sure both Decision Agent and Master Agent servers are running
3. Reload the extension in Chrome
4. The Decision Agent will automatically analyze page sync data

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`

## 🔄 Complete Setup

For the full system to work, you need:

1. **Master Agent** (port 9000) - Already running
   ```bash
   cd Server/master_agent
   python -m master_agent.server
   ```

2. **Decision Agent** (port 8004) - Start this now
   ```bash
   cd Server/decision_agent
   python -m decision_agent.server
   ```

## 🎯 Next Steps

- Read `README.md` for detailed architecture
- Check decision agent logs for analysis results
- Monitor when insurance prompts are forwarded to Master Agent

## 🐛 Troubleshooting

**Server won't start?**
- Check if port 8004 is available: `netstat -ano | findstr :8004` (Windows) or `lsof -i :8004` (Mac/Linux)
- Verify OpenAI API key is set
- Ensure all dependencies installed

**Extension can't connect?**
- Verify server is running: `curl http://localhost:8004/health`
- Check CORS settings in `config.py`
- Review extension console for errors
- Ensure Decision Agent URL in `config.js` matches server port

**Decision Agent not forwarding to Master Agent?**
- Verify Master Agent is running on port 9000
- Check `MASTER_AGENT_URL` in Decision Agent config
- Review Decision Agent logs for forwarding errors

