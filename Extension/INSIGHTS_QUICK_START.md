# 🚀 Quick Start: Insights Integration

## What You Get

When users ask about travel risks, the extension shows a beautiful insights banner at the top with real data:

```
╔══════════════════════════════════════════════════════╗
║ 💡 Insights:                                      × ║
║ Traveling to China? Medical claims average $3,500   ║
║ per incident. Last year, 127 travelers required     ║
║ emergency medical care, with costs reaching         ║
║ $15,000. Don't risk it—secure your travel          ║
║ insurance today.                                    ║
╚══════════════════════════════════════════════════════╝
```

---

## 3-Step Setup

### Step 1: Start Insights API
```bash
cd Server
python start_insights.py
```
✅ Runs on `http://localhost:5000`

### Step 2: Start Insights Agent
```bash
cd Server/insights_agent
python server.py
```
✅ Runs on `http://localhost:8008`

### Step 3: Reload Extension
1. Go to `chrome://extensions/`
2. Find "SingPass Insurance Chat"
3. Click reload 🔄

---

## Test It!

### Open Extension → Try These:

**Will Show Insights Banner:**
```
"What are the medical risks in China?"
"Which destinations have highest claim costs?"
"Should I buy travel insurance for Thailand?"
```

**Won't Show Insights Banner:**
```
"Hello, how are you?"
"What's your name?"
```

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  USER TYPES: "What are medical risks in China?"    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ├─────► Master Agent (port 9000)
                       │       Gets normal chat response
                       │       
                       └─────► Insights Agent (port 8008)
                               ↓
                               Decides: should_analyze = true
                               ↓
                               Calls Start Insights API (port 5000)
                               ↓
                               Generates 3 Cypher queries
                               ↓
                               Executes against Neo4j
                               ↓
                               Analyzes results with GPT
                               ↓
                               Returns persuasive insights
                               
┌─────────────────────────────────────────────────────┐
│  💡 INSIGHTS BANNER APPEARS AT TOP!                │
└─────────────────────────────────────────────────────┘
```

---

## What Was Changed

| File | What Changed |
|------|-------------|
| `sidepanel.html` | Added insights banner element |
| `sidepanel.js` | Added insights fetching & display logic |
| `sidepanel.css` | Added beautiful banner styling |
| `insights_agent/config.py` | Fixed port to 5000 |

---

## Features

✅ **Smart Detection** - AI decides when insights are useful
✅ **Real Data** - From Neo4j travel insurance claims database
✅ **Beautiful UI** - Gradient banner with animations
✅ **Non-Blocking** - Loads after main response
✅ **Dismissible** - X button to close
✅ **Error Resilient** - Chat works even if insights fail

---

## Troubleshooting

### Insights never show?

**Check servers are running:**
```bash
# Check Insights Agent
curl http://localhost:8008/health

# Check Start Insights API
curl http://localhost:5000/health
```

**Check browser console (F12):**
Look for `[Insights]` logs

### Shows for every message?

The Insights Agent might be misconfigured. It should only trigger for travel/risk-related queries.

---

## API Endpoints

Your extension now uses:
- `http://localhost:9000/chat` - Master Agent (main chat)
- `http://localhost:8008/process` - **Insights Agent** ⭐ NEW
- `http://localhost:8007/extract` - PDF Extractor

---

## Example Response

When insights are shown, you'll see in console:

```javascript
[Insights] Decision result: {
  should_analyze: true,
  performed_analytics: true,
  confidence: 0.95,
  reasoning: "Query is about travel risks and would benefit from data analysis"
}
[Insights] Displayed insights banner
```

---

## That's It! 🎉

Your extension now intelligently shows data-driven insights to convince users to buy travel insurance!

**For detailed technical documentation, see:** `INSIGHTS_INTEGRATION.md`



