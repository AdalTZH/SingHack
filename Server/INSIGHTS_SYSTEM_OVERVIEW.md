# 🎯 Insights System Overview

## What Is This?

An intelligent system that automatically determines when to show travel insurance insights to users based on their queries. When users ask about travel risks, destinations, or claim statistics, the system:

1. ✅ **Detects** if the query is insights-worthy (using GPT)
2. ✅ **Analyzes** real travel insurance claims data from Neo4j
3. ✅ **Generates** persuasive insights with real statistics
4. ✅ **Displays** insights prominently in the chat interface

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER EXTENSION                           │
│                    (Chat Interface / Frontend)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ POST /process
                             │ { "query": "What are risks in China?" }
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    INSIGHTS AGENT (Port 8008)                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Step 1: Determine if query needs insights (GPT-4o)       │  │
│  │  - Is this travel/insurance related?                      │  │
│  │  - Would analytics help answer this?                      │  │
│  │  - Would insights be persuasive?                          │  │
│  │  → Returns: should_analyze: true/false                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             │ if should_analyze == true           │
│                             │                                     │
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Step 2: Call Start Insights API                          │  │
│  │  POST http://localhost:5000/query                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                  START INSIGHTS API (Port 5000)                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Step 3: Generate Cypher Queries (GPT-4o)                 │  │
│  │  - Creates 3 different Neo4j queries                      │  │
│  │  - Statistics, patterns, trends                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Step 4: Execute Against Neo4j                            │  │
│  │  - Runs Cypher queries                                    │  │
│  │  - Retrieves claim data                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Step 5: Analyze Results (GPT-5.1)                        │  │
│  │  - Creates persuasive summary                             │  │
│  │  - Highlights risks with real numbers                     │  │
│  │  - 3-4 sentences, punchy, urgent                          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             │ Returns:                            │
│                             │ { analysis: "...", results: [...] } │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                       NEO4J DATABASE                             │
│                 (Travel Insurance Claims Data)                   │
│  - Destinations, Claim Types, Causes of Loss                    │
│  - Real claim amounts (gross_paid)                              │
│  - Relationships between entities                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Flow Example

### Query: "What are the medical risks in China?"

**Step 1: Insights Agent Decision**
```json
{
  "should_analyze": true,
  "reasoning": "Query is about travel risks and would benefit from claims data analysis",
  "confidence": 0.95
}
```

**Step 2: Generate & Execute Cypher Queries**
```cypher
// Query 1: Medical claim statistics for China
MATCH (c:Claim)-[:OCCURRED_IN]->(d:Destination {name: 'China'})
MATCH (c)-[:IS_TYPE]->(ct:ClaimType {name: 'Medical Expense'})
RETURN avg(c.gross_paid) as avg_cost, count(c) as total_claims, max(c.gross_paid) as max_cost

// Query 2: Most common causes
MATCH (c:Claim)-[:OCCURRED_IN]->(d:Destination {name: 'China'})
MATCH (c)-[:CAUSED_BY]->(cause:CauseOfLoss)
RETURN cause.name, count(*) as frequency
ORDER BY frequency DESC
LIMIT 5

// Query 3: Trend analysis
...
```

**Step 3: Analyze Results (GPT-5.1)**
```
Traveling to China? Medical claims average $3,500 per incident. Last year, 127 travelers 
required emergency medical care, with costs reaching $15,000. The most common cause is 
sudden illness, accounting for 68% of claims. Don't risk it—secure your travel insurance today.
```

**Step 4: Display to User**
```
┌────────────────────────────────────────────────────────┐
│ 💡 Insights:                                        × │
│ Traveling to China? Medical claims average $3,500     │
│ per incident. Last year, 127 travelers required       │
│ emergency medical care, with costs reaching $15,000.  │
│ Don't risk it—secure your travel insurance today.     │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Insights Agent
cd Server/insights_agent
pip install -r requirements.txt

# Start Insights API
cd Server
pip install flask neo4j openai
```

### 2. Configure Environment

Create `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key
```

Update Neo4j credentials in `Server/start_insights.py`:
```python
NEO4J_CONFIG = {
    'uri': 'neo4j+s://your-instance.databases.neo4j.io',
    'user': 'neo4j',
    'password': 'your-password'
}
```

### 3. Start Servers

**Terminal 1:**
```bash
cd Server
python start_insights.py
# Runs on http://localhost:5000
```

**Terminal 2:**
```bash
cd Server/insights_agent
python server.py
# Runs on http://localhost:8008
```

### 4. Test Integration

```bash
cd Server/insights_agent
python test_integration.py
```

---

## 💻 Frontend Integration

### Simple Integration (3 steps)

```javascript
// 1. Call the API
const response = await fetch('http://localhost:8008/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: userMessage })
});

const result = await response.json();

// 2. Check if insights should be shown
if (result.should_analyze && result.insights) {
  // 3. Display insights
  displayInsights(result.insights);
}
```

**See `Server/insights_agent/frontend_example.js` for complete code with UI components!**

---

## 📊 Response Format

### When Analytics Performed:
```json
{
  "should_analyze": true,
  "performed_analytics": true,
  "insights": "Traveling to China? Medical claims average $3,500...",
  "reasoning": "Query is about travel risks and would benefit from analysis",
  "confidence": 0.95,
  "query_results": [...],
  "execution_time": "2.3s"
}
```

### When No Analytics Needed:
```json
{
  "should_analyze": false,
  "performed_analytics": false,
  "insights": null,
  "reasoning": "General conversation, not related to travel risks",
  "confidence": 0.9
}
```

---

## ✅ What Triggers Insights?

**YES - These WILL trigger analytics:**
- ✅ "What are the medical risks in China?"
- ✅ "Which destinations have highest claim costs?"
- ✅ "Should I buy travel insurance for Thailand?"
- ✅ "What could go wrong when traveling?"
- ✅ "How much do medical claims cost?"
- ✅ "What are baggage loss statistics?"

**NO - These WON'T trigger analytics:**
- ❌ "Hello, how are you?"
- ❌ "What's your name?"
- ❌ "Tell me about your company"
- ❌ "How do I reset my password?"

---

## 🎨 UI Example

### Insights Banner CSS

```css
.insights-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.insights-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 8px;
}

.insights-content {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
}
```

---

## 🔧 Configuration

### Port Configuration
- **Insights Agent:** Port 8008 (configurable via `INSIGHTS_AGENT_PORT`)
- **Start Insights API:** Port 5000 (hardcoded in `start_insights.py`)

### API URL Configuration
In `Server/insights_agent/config.py`:
```python
INSIGHTS_ANALYTICS_URL = os.getenv('INSIGHTS_ANALYTICS_URL', 'http://localhost:5000')
```

✅ **FIXED:** Now correctly points to port 5000 (was 5001)

---

## 🧪 Testing

### Manual Test:
```bash
curl -X POST http://localhost:8008/process \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the medical risks in Thailand?"}'
```

### Automated Test:
```bash
cd Server/insights_agent
python test_integration.py
```

### Health Checks:
```bash
curl http://localhost:8008/health  # Insights Agent
curl http://localhost:5000/health  # Start Insights API
```

---

## 📁 File Structure

```
Server/
├── start_insights.py              # Analytics API (Port 5000)
├── insights_agent/
│   ├── server.py                  # Insights Agent Server (Port 8008)
│   ├── insights_agent.py          # Core agent logic
│   ├── api.py                     # API wrapper
│   ├── config.py                  # Configuration
│   ├── INTEGRATION_GUIDE.md       # Detailed integration guide
│   ├── frontend_example.js        # Frontend code examples
│   ├── test_integration.py        # Integration tests
│   └── requirements.txt           # Python dependencies
└── INSIGHTS_SYSTEM_OVERVIEW.md    # This file
```

---

## 🔍 How It Works (Technical Details)

### 1. Insights Agent Decision Making
- Uses GPT-4o to analyze query intent
- Considers: travel relevance, data availability, persuasive value
- Returns confidence score (0.0 to 1.0)

### 2. Cypher Query Generation
- GPT-4o generates 3 different Neo4j queries
- Uses actual values from database (destinations, claim types, etc.)
- Focuses on: statistics, patterns, trends

### 3. Neo4j Execution
- Executes Cypher queries against claims database
- Handles Neo4j date/time serialization
- Returns structured results

### 4. Insight Analysis
- GPT-5.1 analyzes query results
- Creates persuasive 3-4 sentence summary
- Emphasizes risks, costs, and urgency
- Uses real numbers for credibility

---

## 🎯 Key Benefits

1. **Automatic Decision Making** - No manual configuration needed
2. **Real Data** - Uses actual travel insurance claims
3. **Persuasive** - Designed to encourage insurance purchases
4. **Flexible** - Works with any travel/insurance related query
5. **Error Resilient** - Gracefully handles failures
6. **Fast** - Typically responds in 2-5 seconds

---

## 🚨 Troubleshooting

### "Connection Refused"
- Ensure both servers are running
- Check ports 5000 and 8008 are not in use

### "No insights returned"
- Verify OpenAI API key is set
- Check Neo4j credentials
- Test with example queries

### "Timeout errors"
- Increase fetch timeout to 30s
- Neo4j queries can take 5-10 seconds
- Show loading state in UI

---

## 📚 Documentation

- **Integration Guide:** `Server/insights_agent/INTEGRATION_GUIDE.md`
- **Frontend Example:** `Server/insights_agent/frontend_example.js`
- **Test Script:** `Server/insights_agent/test_integration.py`
- **This Overview:** `Server/INSIGHTS_SYSTEM_OVERVIEW.md`

---

## 🎉 Ready to Integrate!

1. ✅ Servers are configured correctly (port 5000 fixed)
2. ✅ Integration code examples provided
3. ✅ Test scripts available
4. ✅ Documentation complete

**Next Step:** Integrate with your extension using the examples in `frontend_example.js`!

---

## 💡 Example Usage Flow

```javascript
// In your chat handler
async function onUserMessage(message) {
  // Get insights
  const insights = await fetch('http://localhost:8008/process', {
    method: 'POST',
    body: JSON.stringify({ query: message })
  }).then(r => r.json());
  
  // Display if available
  if (insights.insights) {
    showInsightsBanner(insights.insights);
  }
  
  // Continue with normal chat...
}
```

**That's it!** The system handles everything else automatically. 🚀




