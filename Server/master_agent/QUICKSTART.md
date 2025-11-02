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

## 🎯 Next Steps

- Read `README.md` for detailed architecture
- Explore agent integration examples
- Customize routing logic
- Add new specialized agents

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

