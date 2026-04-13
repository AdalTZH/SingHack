# Insights Agent Integration Guide

## System Architecture

```
┌──────────────┐         ┌──────────────────┐         ┌─────────────────┐
│              │         │                  │         │                 │
│  Extension   │ ──────▶ │ Insights Agent   │ ──────▶ │ Start Insights  │
│  (Frontend)  │         │  (Port 8008)     │         │   (Port 5000)   │
│              │ ◀────── │                  │ ◀────── │                 │
└──────────────┘         └──────────────────┘         └─────────────────┘
                                   │
                                   │ (Determines if 
                                   │  analytics needed)
                                   │
                                   ▼
                         ┌──────────────────┐
                         │     Neo4j        │
                         │   (Claims DB)    │
                         └──────────────────┘
```

## Flow Overview

1. **User Query** → Extension sends query to Insights Agent
2. **Decision Phase** → Insights Agent determines if `should_analyze` is true
3. **Analytics Phase** → If true, calls Start Insights API to generate Cypher queries and get insights
4. **Response** → Extension displays insights at top of chat

---

## API Endpoints

### 1. Insights Agent Server (Port 8008)

**Endpoint:** `POST http://localhost:8008/process`

**Request:**
```json
{
  "query": "What are the medical risks of traveling to China?"
}
```

**Response (when should_analyze = true):**
```json
{
  "should_analyze": true,
  "performed_analytics": true,
  "insights": "Traveling to China? Medical claims average $3,500 per incident. Last year, 127 travelers required emergency medical care, with costs reaching $15,000. Don't risk it—secure your travel insurance today.",
  "reasoning": "Query is about travel risks and would benefit from claims data analysis",
  "confidence": 0.95,
  "query_results": [...],
  "execution_time": "2.3s"
}
```

**Response (when should_analyze = false):**
```json
{
  "should_analyze": false,
  "performed_analytics": false,
  "insights": null,
  "reasoning": "Query is general conversation, not related to travel risks or insurance",
  "confidence": 0.9
}
```

### 2. Start Insights API (Port 5000)

**Note:** This is called internally by Insights Agent. Extension should NOT call this directly.

**Endpoint:** `POST http://localhost:5000/query`

---

## Extension Integration

### Step 1: Send User Query to Insights Agent

```javascript
async function getInsights(userQuery) {
  try {
    const response = await fetch('http://localhost:8008/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userQuery })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching insights:', error);
    return { should_analyze: false, insights: null };
  }
}
```

### Step 2: Check if Insights Should Be Displayed

```javascript
const result = await getInsights(userQuery);

if (result.should_analyze && result.performed_analytics && result.insights) {
  // Display insights at top of chat
  displayInsights(result.insights);
}
```

### Step 3: Display Insights in UI

```javascript
function displayInsights(insightsText) {
  // Create insights banner at top of chat interface
  const insightsElement = document.createElement('div');
  insightsElement.className = 'insights-banner';
  insightsElement.innerHTML = `
    <div class="insights-header">
      <span class="icon">💡</span>
      <span class="title">Insights:</span>
    </div>
    <div class="insights-content">
      ${insightsText}
    </div>
  `;
  
  // Insert at top of chat
  chatContainer.insertBefore(insightsElement, chatContainer.firstChild);
}
```

### Step 4: Example CSS for Insights Display

```css
.insights-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.insights-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.insights-header .icon {
  font-size: 18px;
}

.insights-content {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
}
```

---

## Running the Servers

### Start Both Services:

**Terminal 1 - Start Insights API (Port 5000):**
```bash
cd Server
python start_insights.py
```

**Terminal 2 - Start Insights Agent (Port 8008):**
```bash
cd Server/insights_agent
python server.py
```

### Environment Variables:

Create a `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
TEMPERATURE=0.7
INSIGHTS_ANALYTICS_URL=http://localhost:5000
INSIGHTS_AGENT_PORT=8008
```

---

## Testing

### Test Insights Agent:

```bash
curl -X POST http://localhost:8008/process \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the medical risks in Thailand?"}'
```

### Test Health Checks:

```bash
# Insights Agent
curl http://localhost:8008/health

# Start Insights API
curl http://localhost:5000/health
```

---

## Example Queries That SHOULD Trigger Analytics:

✅ "What are the medical risks of traveling to China?"
✅ "Which destinations have the highest claim costs?"
✅ "Should I buy travel insurance for Thailand?"
✅ "What could go wrong when traveling to Europe?"
✅ "How much do medical claims cost on average?"

## Example Queries That SHOULD NOT Trigger Analytics:

❌ "Hello, how are you?"
❌ "What's your name?"
❌ "How do I reset my password?"
❌ "Tell me about your company"

---

## Error Handling

```javascript
async function getInsightsWithErrorHandling(userQuery) {
  try {
    const response = await fetch('http://localhost:8008/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userQuery }),
      timeout: 30000 // 30 second timeout
    });
    
    if (!response.ok) {
      console.error('Insights API error:', response.status);
      return { should_analyze: false, insights: null };
    }
    
    const data = await response.json();
    
    // Check for errors in response
    if (data.error) {
      console.error('Insights error:', data.error);
      return { should_analyze: false, insights: null };
    }
    
    return data;
    
  } catch (error) {
    console.error('Failed to fetch insights:', error);
    // Don't show insights on error, just continue normally
    return { should_analyze: false, insights: null };
  }
}
```

---

## Complete Flow Example

```javascript
// In your chat message handler
async function handleUserMessage(userMessage) {
  // 1. Get insights
  const insightsResult = await getInsights(userMessage);
  
  // 2. If insights should be shown, display them
  if (insightsResult.should_analyze && 
      insightsResult.performed_analytics && 
      insightsResult.insights) {
    displayInsights(insightsResult.insights);
  }
  
  // 3. Continue with normal chat flow
  sendMessageToChat(userMessage);
  
  // Optional: Log decision
  console.log('Insights Decision:', {
    should_analyze: insightsResult.should_analyze,
    performed_analytics: insightsResult.performed_analytics,
    confidence: insightsResult.confidence,
    reasoning: insightsResult.reasoning
  });
}
```

---

## Troubleshooting

### Issue: "Connection Refused"
- Ensure both servers are running
- Check ports 5000 and 8008 are not in use
- Verify URLs in config.py

### Issue: "No insights returned"
- Check OpenAI API key is set
- Verify Neo4j credentials in start_insights.py
- Test with example queries that should trigger analytics

### Issue: "Timeout errors"
- Neo4j queries can take 5-10 seconds
- Set appropriate timeout in fetch (30s recommended)
- Consider showing loading state in UI

---

## Key Points

1. ✅ **Port Configuration Fixed** - Now correctly points to port 5000
2. ✅ **Two-Server Architecture** - Insights Agent (8008) + Start Insights (5000)
3. ✅ **Automatic Decision Making** - Agent decides when to show insights
4. ✅ **Error Resilient** - Falls back gracefully if analytics fail
5. ✅ **Frontend Integration** - Simple POST request, check flag, display insights




