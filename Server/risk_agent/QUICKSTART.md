# Risk Agent Quick Start

Get the Risk Agent running in 3 steps!

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
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
GDACS_ENABLED=true
```

**Note:** API keys are optional. The agent will work with basic functionality even without them, but risk assessment will be limited.

### 3️⃣ Start the Server

```bash
python -m risk_agent.server
```

Server will start at `http://localhost:8003`

## 🧪 Test the API

### Using curl

```bash
# Health check
curl http://localhost:8003/health

# Assess risk for a destination
curl -X POST http://localhost:8003/assess_risk \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Traveling to Japan",
    "destination": "Japan",
    "departure_date": "2025-03-15",
    "return_date": "2025-03-25",
    "activities": ["hiking", "sightseeing"]
  }'
```

### Using Python

```python
import requests

# Assess risk
response = requests.post(
    'http://localhost:8003/assess_risk',
    json={
        'query': 'Traveling to Tokyo',
        'destination': 'Tokyo, Japan',
        'departure_date': '2025-03-15',
        'return_date': '2025-03-25',
        'activities': ['hiking', 'sightseeing']
    }
)

print(response.json())
```

## 🌐 Connect to Master Agent

The Master Agent is already configured to use the Risk Agent at `http://localhost:8003`

1. Start the Risk Agent:
   ```bash
   python -m risk_agent.server
   ```

2. Start the Master Agent:
   ```bash
   python -m master_agent.server
   ```

3. Send queries to Master Agent about travel risks!

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## 🎯 Endpoints

- `GET /health` - Health check
- `POST /assess_risk` - Comprehensive risk assessment
- `GET /weather` - Get weather forecast
- `GET /disasters` - Check natural disasters
- `GET /advisories` - Check travel advisories

## 🔍 What the Risk Agent Does

The Risk Agent assesses travel risks in multiple categories:

1. **Weather Risks** - Severe weather conditions (thunderstorms, heavy rain, high winds, extreme temperatures)
2. **Natural Disasters** - Active alerts from GDACS (earthquakes, tsunamis, typhoons, floods, volcanoes, wildfires)
3. **Travel Advisories** - Government travel warnings and advisories
4. **Activity Risks** - Activity-specific safety concerns

## 🐛 Troubleshooting

**Server won't start?**
- Check if port 8003 is available
- Verify dependencies are installed
- Check logs for errors

**API errors?**
- Verify API keys are set correctly in `.env` or environment variables
- Check API rate limits
- Ensure internet connectivity for API calls

**Risk Agent not responding from Master Agent?**
- Verify Risk Agent is running: `curl http://localhost:8003/health`
- Check `RISK_AGENT_URL` in Master Agent config
- Review Risk Agent logs for errors

## 📚 Next Steps

- Read `README.md` for detailed MCP server information
- Check risk assessment results
- Customize risk assessment settings in `config.py`
- Monitor when risk assessments are triggered by Master Agent

## 🌍 Example Queries to Master Agent

Once both agents are running, try these queries with the Master Agent:

- "What are the risks of traveling to Japan?"
- "Is it safe to go to Tokyo in March?"
- "What natural disasters should I be aware of in Japan?"
- "I'm planning to go hiking in Japan, what are the risks?"
- "Are there any travel advisories for Japan?"

