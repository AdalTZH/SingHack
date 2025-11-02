# SingHack Backend - Multi-Agent Travel Insurance System

A sophisticated multi-agent AI system for conversational travel insurance, built for the **Ancileo × MSIG Conversational Insurance Challenge**. This system transforms traditional insurance purchasing from a tedious form-filling process into an engaging, intelligent dialogue powered by multiple specialized AI agents.

## 🎯 Project Overview

SingHack Backend is a comprehensive travel insurance platform that leverages a multi-agent architecture to provide intelligent, conversational insurance assistance. The system consists of:

- **Chrome Extension** - Modern browser-based UI for user interactions
- **Master Agent** - Central orchestration system that routes queries and synthesizes responses
- **Specialized AI Agents** - Four domain-specific agents handling different aspects of insurance assistance
- **Payment System** - Stripe integration for seamless payment processing
- **Decision Engine** - Page analysis system that proactively offers insurance recommendations

### Key Innovation

Instead of requiring users to fill out lengthy forms, users can:
- **Chat naturally** about insurance needs
- **Upload documents** (flight confirmations, itineraries) and get instant quotes
- **Ask questions** and receive detailed answers with policy citations
- **Get proactive recommendations** while browsing travel websites
- **Complete purchases** without leaving the conversation

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Extension                          │
│  - Sidebar chat interface                                    │
│  - Page sync analysis                                        │
│  - Modern UI with real-time responses                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                         │
        ↓                         ↓
┌──────────────────┐    ┌──────────────────────┐
│  Decision Agent  │    │   Master Agent       │
│  Port: 8004      │    │   Port: 9000         │
│  - Page Analysis │    │   - Orchestration    │
│  - Auto-prompts  │    │   - Query Routing   │
└──────────────────┘    │   - Response Synth   │
                        └───────┬──────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ↓           ↓           ↓
            ┌───────────┐ ┌──────────┐ ┌──────────┐
            │Classifier │ │ Predict  │ │   Risk   │
            │  Agent    │ │  Agent   │ │  Agent   │
            │ - Compare │ │ - Plans  │ │ - Weather│
            │ - Explain │ │ - Claims │ │ - Alerts │
            │ - Eligibility│ - Scores │ │ - Advisories│
            └───────────┘ └──────────┘ └──────────┘
                    │           │           │
                    └───────────┴───────────┘
                                │
                        ┌───────┴────────┐
                        │  Data Sources  │
                        │ - Taxonomy DB  │
                        │ - Claims DB    │
                        │ - External APIs│
                        └────────────────┘
```

## 📦 Components

### 1. Chrome Extension (`Extension/`)

A modern browser extension that provides the user interface for the insurance system.

**Features:**
- Sidebar chat interface with clean, gradient-based design
- Real-time message handling
- Dual mode: Master Agent orchestration or direct OpenAI
- Page sync analysis for proactive insurance prompts
- Secure API key storage

**Key Files:**
- `background.js` - Service worker handling API calls
- `sidepanel.js` - Chat interface logic
- `config.js` - Configuration (API keys, agent URLs)

**Documentation:** See `Extension/README.md`

### 2. Master Agent (`Server/master_agent/`)

Central orchestration system that routes queries to specialized agents and synthesizes responses.

**Features:**
- FastAPI server on port 9000
- LangGraph workflow orchestration
- Intelligent query routing
- Multi-agent response synthesis
- REST API for Chrome extension integration

**Capabilities:**
- Routes queries to appropriate specialized agents
- Combines multiple agent responses into coherent answers
- Provides unified API endpoint for the extension
- Handles error recovery and fallbacks

**API Endpoints:**
- `POST /chat` - Main chat endpoint
- `GET /health` - Health check
- `GET /agents` - List available agents
- `GET /docs` - Swagger documentation

**Documentation:** See `Server/master_agent/README.md` and `Server/master_agent/QUICKSTART.md`

### 3. Decision Agent (`Server/decision_agent/`)

Analyzes page sync data from Chrome extension to determine when to offer insurance.

**Features:**
- FastAPI server on port 8004
- LLM-powered page content analysis
- Automatic insurance prompt generation
- Confidence scoring for recommendations
- Stripe payment page detection (skips analysis)

**Workflow:**
1. Receives page sync data (URL, title, HTML content)
2. Analyzes content using OpenAI LLM
3. Determines if travel insurance is relevant
4. Forwards insurance prompts to Master Agent when appropriate

**Documentation:** See `Server/decision_agent/README.md` and `Server/decision_agent/QUICKSTART.md`

### 4. Classifier Agent (`Server/classifier_agent/`)

Classifies user insurance queries into structured types using LangGraph and taxonomy data.

**Features:**
- LangGraph workflow orchestration
- Query classification into 4 types:
  - **Comparison** - Compare products/benefits
  - **Explanation** - Understand coverage details
  - **Eligibility** - Check coverage eligibility
  - **Scenario Analysis** - Analyze hypothetical situations
- Taxonomy data integration
- MCP server for AI assistant integration
- Entity extraction (products, benefits, keywords)

**Documentation:** See `Server/classifier_agent/README.md`

### 5. Predict Agent (`Server/predict_agent/`)

Recommends insurance plans based on historical claims data and user profiles.

**Features:**
- PostgreSQL database integration
- Claims data analysis
- Destination-specific product performance
- Risk-adjusted scoring
- User profile matching
- MCP server for AI assistant integration

**Capabilities:**
- Find suitable insurance plans based on trip details
- Get product performance statistics
- Analyze destination coverage
- Score products based on historical claims patterns

**Documentation:** See `Server/predict_agent/README.md`

### 6. Risk Agent (`Server/risk_agent/`)

Assesses travel risks using weather data, disaster alerts, and travel advisories.

**Features:**
- OpenWeatherMap integration
- GDACS natural disaster alerts
- Tavily web search for travel risks
- Government travel advisory checking
- MCP server with 6 risk assessment tools
- Comprehensive risk scoring

**Tools:**
1. `get_weather_forecast` - Weather forecasts for destinations
2. `check_severe_weather` - Severe weather conditions
3. `check_natural_disasters` - Natural disaster alerts
4. `web_search_risks` - Web-based risk information
5. `comprehensive_risk_search` - Multi-category risk search
6. `check_travel_advisories` - Government advisories

**Documentation:** See `Server/risk_agent/README.md`

### 7. Payment System (`Payments/`)

Stripe payment integration with webhook handling and DynamoDB storage.

**Features:**
- Docker Compose setup for local development
- Stripe checkout session creation
- Webhook event processing
- DynamoDB payment record storage
- Success/cancel page handling
- Payment status tracking

**Services:**
- DynamoDB Local (port 8000)
- DynamoDB Admin UI (port 8010)
- Stripe Webhook Service (port 8086)
- Payment Pages (port 8085)

**Documentation:** See `Payments/README.md`

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for Chrome extension development)
- Docker (for payment system)
- OpenAI API key
- PostgreSQL database (for Predict Agent)
- Weather API keys (for Risk Agent)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SingHack-Backend
```

2. **Install Server Dependencies**
```bash
cd Server
pip install -r requirements.txt
```

3. **Configure Environment**

Create `.env` file in `Server/` directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Master Agent Configuration
MASTER_AGENT_HOST=0.0.0.0
MASTER_AGENT_PORT=9000

# Database Configuration (for Predict Agent)
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# API Keys (for Risk Agent)
OPENWEATHER_API_KEY=your_openweather_key
TAVILY_API_KEY=your_tavily_key
```

4. **Start Master Agent Server**
```bash
cd Server
python -m master_agent.server
```

Server will be available at `http://localhost:9000`

5. **Start Decision Agent (Optional, for page sync)**
```bash
cd Server
python -m decision_agent.server
```

6. **Configure Chrome Extension**

Edit `Extension/config.js`:
```javascript
const CONFIG = {
    USE_MASTER_AGENT: true,
    MASTER_AGENT_URL: 'http://localhost:9000',
    DECISION_AGENT_URL: 'http://localhost:8004',
    OPENAI_API_KEY: 'your_key'  // For fallback
};
```

7. **Load Chrome Extension**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `Extension` folder

8. **Start Payment System (Optional)**
```bash
cd Payments
# Create .env file with STRIPE_WEBHOOK_SECRET
docker-compose up -d
```

### Verification

Test the system:
```bash
# Test Master Agent
curl http://localhost:9000/health

# Test chat endpoint
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which insurance plan is best for Japan?"}'
```

## 📊 System Workflow

### 1. Chat Query Flow

```
User Message (Extension)
    ↓
Master Agent (Port 9000)
    ↓
Query Routing Analysis
    ├─ Comparison/Explanation → Classifier Agent
    ├─ Recommendation → Predict Agent
    └─ Risk Assessment → Risk Agent
    ↓
Response Synthesis (OpenAI)
    ↓
Final Answer (Extension)
```

### 2. Page Sync Flow

```
User Browses Travel Website
    ↓
Chrome Extension Captures Page Data
    ↓
Decision Agent (Port 8004)
    ↓
LLM Analysis (Travel-related?)
    ├─ Yes → Generate Insurance Prompt → Master Agent
    └─ No → Skip
    ↓
Insurance Recommendation (Extension)
```

### 3. Multi-Agent Coordination

The Master Agent uses **Agent-to-Agent (A2A) protocol** to communicate with specialized agents:

- **Direct Import** - Agents imported as Python modules (fast, synchronous)
- **REST API** - Agents as separate HTTP services (scalable, distributed)
- **MCP Protocol** - Model Context Protocol for AI assistant integration

## 🔧 Configuration

### Port Allocation

| Service | Port | Purpose |
|---------|------|---------|
| Master Agent | 9000 | Central orchestration |
| Decision Agent | 8004 | Page analysis |
| Risk Agent | 8003 | Risk assessment (reserved) |
| Classifier Agent | 8001 | Query classification (reserved) |
| Predict Agent | 8002 | Recommendations (reserved) |
| DynamoDB Local | 8000 | Payment storage |
| DynamoDB Admin | 8010 | Payment UI |
| Payment Pages | 8085 | Success/cancel pages |
| Stripe Webhook | 8086 | Payment events |

### Environment Variables

Key environment variables needed:

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for LLM operations

**Optional:**
- `OPENWEATHER_API_KEY` - Weather data for Risk Agent
- `TAVILY_API_KEY` - Web search for Risk Agent
- Database credentials for Predict Agent
- `STRIPE_WEBHOOK_SECRET` - Payment webhooks

## 📚 Documentation

### Main Documentation
- **This README** - Project overview and quick start
- **SETUP_GUIDE.md** - Detailed setup instructions
- **AGENTIC_ARCHITECTURE.md** - Architecture diagrams and workflows

### Agent Documentation
- `Server/master_agent/README.md` - Master Agent API reference
- `Server/master_agent/QUICKSTART.md` - Master Agent quick start
- `Server/decision_agent/README.md` - Decision Agent guide
- `Server/classifier_agent/README.md` - Classifier Agent documentation
- `Server/predict_agent/README.md` - Predict Agent guide
- `Server/risk_agent/README.md` - Risk Agent documentation

### Component Documentation
- `Extension/README.md` - Chrome Extension setup
- `Payments/README.md` - Payment system guide
- `Server/README.md` - Server overview

### Implementation Summaries
- `MASTER_AGENT_SUMMARY.md` - Master Agent implementation details
- `IMPLEMENTATION_SUMMARY.md` - Overall system implementation

## 🧪 Testing

### Test All Agents
```bash
cd Server
python test_agents.py
```

### Test Master Agent
```bash
cd Server
python test_master_agent.py
```

### Test Individual Agents
```bash
python -m classifier_agent.example_usage
python -m predict_agent.example_usage
python -m risk_agent.example_usage
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:9000/health

# Chat endpoint
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare Product A and Product B"}'

# Swagger docs
open http://localhost:9000/docs
```

## 🎯 Use Cases

### 1. Conversational Insurance Queries

**User:** "Which plan has better medical coverage?"

**System Flow:**
1. Master Agent receives query
2. Routes to Classifier Agent (comparison query)
3. Classifier analyzes taxonomy data
4. Returns comparison with citations
5. Master Agent synthesizes response
6. User receives detailed comparison

### 2. Insurance Recommendations

**User:** "I'm traveling to Japan for skiing in March. What insurance should I get?"

**System Flow:**
1. Master Agent receives query
2. Routes to Predict Agent (recommendation)
3. Routes to Risk Agent (risk assessment)
4. Predict Agent analyzes claims data
5. Risk Agent checks weather/disasters
6. Master Agent synthesizes comprehensive recommendation

### 3. Proactive Insurance Offers

**User:** Browses travel booking website

**System Flow:**
1. Chrome Extension captures page data
2. Sends to Decision Agent
3. Decision Agent analyzes: travel-related?
4. If yes, generates insurance prompt
5. Forwards to Master Agent
6. Extension shows proactive recommendation

## 🛠️ Development

### Project Structure

```
SingHack-Backend/
├── Extension/                  # Chrome Extension
│   ├── background.js          # Service worker
│   ├── sidepanel.js           # Chat UI
│   ├── config.js              # Configuration
│   └── README.md
│
├── Server/                     # Backend Services
│   ├── master_agent/          # Central orchestration
│   │   ├── server.py          # FastAPI server
│   │   ├── master_agent.py    # LangGraph workflow
│   │   ├── agent_client.py    # A2A communication
│   │   └── README.md
│   │
│   ├── decision_agent/        # Page analysis
│   │   ├── server.py
│   │   ├── decision_agent.py
│   │   └── README.md
│   │
│   ├── classifier_agent/      # Query classification
│   │   ├── classifier_agent.py
│   │   ├── taxonomy_loader.py
│   │   ├── mcp_server.py
│   │   └── README.md
│   │
│   ├── predict_agent/         # Insurance recommendations
│   │   ├── predict_agent.py
│   │   ├── database.py
│   │   ├── mcp_server.py
│   │   └── README.md
│   │
│   ├── risk_agent/           # Risk assessment
│   │   ├── mcp_server.py
│   │   └── README.md
│   │
│   ├── requirements.txt       # Dependencies
│   ├── Taxonomy_Hackathon.json
│   └── README.md
│
├── Payments/                  # Payment System
│   ├── docker-compose.yaml
│   ├── webhook/              # Stripe webhook handler
│   ├── payment_pages/         # Success/cancel pages
│   └── README.md
│
├── README.md                  # This file
├── SETUP_GUIDE.md            # Setup instructions
├── AGENTIC_ARCHITECTURE.md   # Architecture docs
└── MASTER_AGENT_SUMMARY.md   # Implementation summary
```

### Key Technologies

- **FastAPI** - Modern Python web framework
- **LangGraph** - Workflow orchestration for agents
- **LangChain** - LLM integration framework
- **OpenAI GPT** - Large language models
- **PostgreSQL** - Claims data database
- **DynamoDB** - Payment record storage
- **Stripe** - Payment processing
- **MCP (Model Context Protocol)** - AI assistant integration
- **Chrome Extension APIs** - Browser integration

### Adding New Agents

To add a new specialized agent:

1. Create agent directory in `Server/`
2. Implement agent logic with API interface
3. Add MCP server (optional)
4. Register with Master Agent
5. Update routing logic in `master_agent.py`

## 🐛 Troubleshooting

### Server Won't Start

**Problem:** Port 9000 already in use
```bash
# Windows
netstat -ano | findstr :9000
# Mac/Linux
lsof -i :9000
```

**Solution:** Kill the process or change port in `config.py`

### Extension Can't Connect

**Problem:** CORS errors
- Check `ALLOWED_ORIGINS` in Master Agent config
- Verify extension URL matches allowed origins

**Problem:** Connection refused
- Verify server is running: `curl http://localhost:9000/health`
- Check firewall settings

### Agent Communication Fails

**Problem:** Import errors
- Verify all agents are in `Server/` directory
- Check Python path includes `Server/`

**Problem:** API timeouts
- Check network connectivity
- Verify specialized agents are running
- Review logs for specific errors

### Database Connection Issues

**Problem:** Predict Agent can't connect
- Verify database credentials in `.env`
- Check database is accessible
- Test connection: `python -c "from predict_agent.database import DatabaseConnection; db = DatabaseConnection(); print(db.connect())"`

## 📈 Future Enhancements

### Short Term
- [ ] Response caching for common queries
- [ ] Session management and conversation history
- [ ] Request throttling and rate limiting
- [ ] Enhanced error messages and recovery

### Medium Term
- [ ] Streaming responses for real-time updates
- [ ] Multi-turn conversation support
- [ ] User authentication and profiles
- [ ] Admin dashboard and monitoring
- [ ] Analytics and usage metrics

### Long Term
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Kubernetes orchestration for scaling
- [ ] Multi-tenant support
- [ ] Advanced ML models for personalization
- [ ] Integration with additional data sources

## 🤝 Contributing

This project was built for the **Ancileo × MSIG Conversational Insurance Challenge**. For contributions or questions:

1. Review the architecture documentation
2. Check existing agent implementations for patterns
3. Follow the existing code structure
4. Add comprehensive documentation
5. Include tests for new features

## 📄 License

This project is part of the Ancileo × MSIG Hackathon submission.

## 🎉 Acknowledgments

Built for the **Ancileo × MSIG Conversational Insurance Challenge** - Transforming insurance from forms to conversations.

---

## 🚀 Get Started Now

1. **Install dependencies**: `cd Server && pip install -r requirements.txt`
2. **Configure environment**: Set up `.env` file with API keys
3. **Start Master Agent**: `python -m master_agent.server`
4. **Load Extension**: Follow Chrome extension setup guide
5. **Start Chatting**: Open the extension and ask insurance questions!

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

For architecture details, see [Server/AGENTIC_ARCHITECTURE.md](Server/AGENTIC_ARCHITECTURE.md)

---

**Built with ❤️ for the future of conversational insurance**
