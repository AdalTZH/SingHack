# Summary Agent Integration

## Overview

The Summary Agent is a microservice that extracts key information from travel-related page content and provides context to the Master Agent for personalized insurance recommendations. This document describes the complete integration flow.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browses Web                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Extension (content.js)                        │
│  - Extracts page content (innerText)                            │
│  - Sends to Decision Agent via background.js                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Agent (Port 8004)                    │
│  - Analyzes if page is travel-related                           │
│  - Returns: should_prompt, persuasion_message, inner_text       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                ┌─────────┴─────────┐
                │   should_prompt?   │
                └─────────┬─────────┘
                          │ YES
                          ▼
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│  Show Cursor     │              │  Summary Agent   │
│  Textbox         │              │  (Port 8020)     │
│  (10 seconds)    │              │  - Extracts key  │
└──────────────────┘              │    information   │
                                  │  - Returns       │
                                  │    summary       │
                                  └─────────┬────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │  localStorage    │
                                  │  page_summaries  │
                                  │  (max 10)        │
                                  └─────────┬────────┘
                                            │
                                            ▼
                          ┌─────────────────────────────┐
                          │  User opens chatbot         │
                          └─────────┬───────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────────────┐
                          │  Master Agent (Port 9000)   │
                          │  - Receives page_summaries  │
                          │  - Provides personalized    │
                          │    recommendations          │
                          └─────────────────────────────┘
```

## Process Flow (Detailed)

### 1. Page Browsing & Content Extraction

**Location:** `Extension/content.js`

When a user browses a web page:
- Extension extracts `innerText` from the page
- Logs character count being sent: `console.log('📊 Character count sent to Decision Agent: X characters')`
- Sends to Decision Agent via `background.js`

### 2. Decision Agent Analysis

**Location:** `Server/decision_agent/decision_agent.py`

Decision Agent:
- Receives page content (truncated to 10k characters)
- Analyzes if page is travel-related
- Returns response with:
  - `should_prompt` (boolean)
  - `persuasion_message` (string, max 20 words)
  - `inner_text` (string, truncated to 10k chars)
  - `travel_context` (string, e.g., "international flight")
  - Other metadata

### 3. Cursor Textbox Display

**Location:** `Extension/content.js`

If `should_prompt=true`:
- Display persuasion message in cursor textbox
- Stream text with animation
- Auto-hide after 10 seconds

### 4. Summary Agent Call

**Location:** `Extension/content.js` → `callSummaryAgent()`

If `should_prompt=true`:
- Extension sends request to `background.js` (to bypass CORS)
- Background script calls Summary Agent at `http://localhost:8020/summarize`
- Sends:
  - `inner_text` (from Decision Agent response)
  - `url`
  - `title`
  - `travel_context`

**Why through background.js?**
- Content scripts cannot make direct requests to localhost due to CORS restrictions
- Background scripts bypass CORS and can make requests to any URL
- Same pattern used for Decision Agent requests

**Location:** `Server/summary_agent/summary_agent.py`

Summary Agent:
- Extracts key information:
  - Travel Type
  - Destination
  - Dates
  - Booking Details
  - Activities
  - Important Details
- Returns concise summary (max 200 words)

### 5. Store Summary in chrome.storage

**Location:** `Extension/content.js` → `storePageSummary()`

- Stores summary in `chrome.storage.local.page_summaries`
- **Important:** Uses `chrome.storage.local` (NOT `localStorage`) to share data between content script and sidepanel
- Keeps last 10 summaries (FIFO)
- Each summary contains:
  ```json
  {
    "summary": "Travel Type: Flight\nDestination: Tokyo...",
    "url": "https://example.com/flights",
    "title": "Flight Booking",
    "travel_context": "international flight",
    "metadata": {...},
    "timestamp": "2024-12-03T10:00:00Z"
  }
  ```

**Why chrome.storage instead of localStorage?**
- Content scripts access **page's localStorage** (e.g., google.com localStorage)
- Sidepanel accesses **extension's localStorage** (isolated)
- They cannot share data via localStorage!
- `chrome.storage.local` is shared across all extension contexts ✅

### 6. Master Agent Integration

**Location:** `Extension/sidepanel.js` → `sendMessage()`

When user opens chatbot and sends a message:
- Load `page_summaries` from `chrome.storage.local`
- Send to Master Agent with request:
  ```json
  {
    "message": "I need travel insurance",
    "conversation_history": [...],
    "document_summaries": [...],
    "page_summaries": [...]
  }
  ```

**Location:** `Server/master_agent/master_agent.py`

Master Agent:
- Receives `page_summaries` in state
- Includes summaries in system prompt
- Provides personalized recommendations based on:
  - User's browsing history (travel pages)
  - Uploaded documents (PDFs)
  - Conversation history

## API Endpoints

### Summary Agent

**POST** `http://localhost:8020/summarize`

Request:
```json
{
  "inner_text": "Page content...",
  "url": "https://example.com/flights",
  "title": "Flight Booking",
  "travel_context": "international flight"
}
```

Response:
```json
{
  "success": true,
  "summary": "**Travel Type**: International Flight\n**Destination**: Tokyo, Japan\n**Dates**: Dec 15-22, 2024\n**Key Details**:\n- Flight: SQ123\n- Price: $850",
  "url": "https://example.com/flights",
  "title": "Flight Booking",
  "travel_context": "international flight",
  "metadata": {
    "model": "gpt-4o-mini",
    "summary_length": 185,
    "content_length": 5230
  }
}
```

### Decision Agent (Updated)

**POST** `http://localhost:8004/analyze`

Response now includes `inner_text`:
```json
{
  "success": true,
  "should_prompt": true,
  "persuasion_message": "Protect your adventure! Travel insurance = peace of mind ✈️",
  "inner_text": "Truncated page content (10k chars)...",
  "travel_context": "international flight",
  ...
}
```

### Master Agent (Updated)

**POST** `http://localhost:9000/chat`

Request now accepts `page_summaries`:
```json
{
  "message": "I need travel insurance",
  "conversation_history": [...],
  "document_summaries": [...],
  "page_summaries": [
    {
      "summary": "...",
      "url": "...",
      "title": "...",
      "travel_context": "...",
      "metadata": {...}
    }
  ]
}
```

## Server Startup

### Start All Servers

```bash
# Terminal 1: Decision Agent
cd Server
python start_decision_agent.py

# Terminal 2: Summary Agent
cd Server
python start_summary_agent.py

# Terminal 3: Master Agent
cd Server
python start_master_agent.py
```

### Verify Servers

```bash
# Decision Agent
curl http://localhost:8004/health

# Summary Agent
curl http://localhost:8020/health

# Master Agent
curl http://localhost:9000/health
```

## Configuration

### Environment Variables

Create `.env` file in `Server/` directory:

```bash
# OpenAI API Key (required for all agents)
OPENAI_API_KEY=your_api_key_here

# Decision Agent
DECISION_AGENT_PORT=8004
OPENAI_MODEL=gpt-4o-mini

# Summary Agent
SUMMARY_AGENT_PORT=8020
SUMMARY_TEMPERATURE=0.3
SUMMARY_MAX_TOKENS=300

# Master Agent
MASTER_AGENT_PORT=9000
```

## Testing

### 1. Test Decision Agent

Browse a travel website (e.g., Skyscanner, Booking.com):
- Check console: `📊 Character count sent to Decision Agent: X characters`
- Verify cursor textbox appears with persuasion message
- Should auto-hide after 10 seconds

### 2. Test Summary Agent

After browsing travel pages:
- Open browser DevTools Console
- Check logs: `📝 Calling Summary Agent for page summary...`
- Check logs: `✅ Summary generated successfully`
- Verify localStorage: `localStorage.getItem('page_summaries')`

### 3. Test Master Agent Integration

Open chatbot in sidepanel:
- Check console: `[Page Summaries] Loaded from localStorage: X summaries`
- Ask: "What travel insurance do I need?"
- Master Agent should reference your browsing history
- Example: "I see you've been looking at flights to Tokyo..."

## Troubleshooting

### Summary Agent not called

**Issue:** Summary Agent is not being called after Decision Agent responds

**Check:**
1. Decision Agent returns `should_prompt=true`
2. Decision Agent returns `inner_text` in response
3. Console shows: `📝 Calling Summary Agent for page summary...`
4. Summary Agent server is running on port 8020

### Summaries not stored

**Issue:** Summaries not appearing in localStorage

**Check:**
1. Console shows: `✅ Summary generated successfully`
2. Console shows: `📦 Stored page summary in localStorage`
3. Check localStorage: `localStorage.getItem('page_summaries')`
4. Check for errors in console

### Master Agent not using summaries

**Issue:** Master Agent doesn't reference browsing history

**Check:**
1. Sidepanel console shows: `[Page Summaries] Loaded from localStorage: X summaries`
2. Request body includes `page_summaries` field
3. Master Agent server logs show: `🌐 Page summaries available: X page(s)`

### Character count issues

**Issue:** Decision Agent receiving too much or too little text

**Check:**
1. Console shows: `📊 Character count sent to Decision Agent: X characters`
2. Decision Agent truncates to 10k characters
3. If 10k is not enough, increase in `Server/decision_agent/decision_agent.py` (line 140)

## Concurrency Considerations

**Q:** What if user sends a new message while Summary Agent is processing?

**A:** This is handled gracefully:
- Summary Agent call is async and non-blocking
- Multiple summaries can be generated concurrently
- Each summary is stored independently in localStorage
- Master Agent receives all accumulated summaries

**Q:** What if multiple tabs trigger summaries?

**A:** Each tab has its own content script instance:
- Summaries from all tabs accumulate in localStorage
- localStorage limit: 10 most recent summaries (FIFO)
- Duplicates are not filtered (each page visit creates a new summary)

## Key Features

1. **Automatic Summary Generation**: No user action required
2. **Persistent Storage**: Summaries stored in localStorage across sessions
3. **Limited Storage**: Only last 10 summaries kept (prevents localStorage overflow)
4. **Concurrency Safe**: Multiple summaries can be generated simultaneously
5. **Character Count Logging**: Console shows exact character count sent to Decision Agent
6. **Detailed Summaries**: Extracts booking details, dates, destinations, activities
7. **Personalized Recommendations**: Master Agent uses browsing history for context

## Example Flow

1. **User browses Skyscanner for Tokyo flight**
   - Console: `📊 Character count sent to Decision Agent: 8523 characters`
   - Textbox: "Planning a trip? Travel insurance keeps you covered! ✈️"
   - Summary stored: "Flight to Tokyo, Dec 15-22, $850, 2 passengers"

2. **User browses hotel booking site**
   - Console: `📊 Character count sent to Decision Agent: 6234 characters`
   - Textbox: "Protect your hotel booking with travel insurance!"
   - Summary stored: "Hotel in Shibuya, 7 nights, $1200"

3. **User opens chatbot**
   - Console: `[Page Summaries] Loaded from localStorage: 2 summaries`
   - User: "What insurance do I need?"
   - Master Agent: "Based on your plans to visit Tokyo from Dec 15-22, staying at a hotel in Shibuya, I recommend..."

## Files Modified/Created

### Created Files
- `Server/summary_agent/__init__.py`
- `Server/summary_agent/config.py`
- `Server/summary_agent/summary_agent.py`
- `Server/summary_agent/api.py`
- `Server/summary_agent/server.py`
- `Server/summary_agent/requirements.txt`
- `Server/summary_agent/README.md`
- `Server/start_summary_agent.py`
- `SUMMARY_AGENT_INTEGRATION.md` (this file)

### Modified Files
- `Server/decision_agent/server.py` - Added `inner_text` to response
- `Server/master_agent/master_agent.py` - Added `page_summaries` to state
- `Server/master_agent/server.py` - Added `page_summaries` to API
- `Extension/content.js` - Added Summary Agent call and localStorage storage
- `Extension/sidepanel.js` - Added `page_summaries` to Master Agent requests

## Notes

- Summary Agent uses GPT-4o-mini for cost efficiency
- Summaries are max 200 words (configurable in `summary_agent.py`)
- Decision Agent truncates page content to 10k characters (configurable in `decision_agent.py`)
- localStorage stores max 10 summaries (configurable in `content.js`)
- Summary Agent runs on port 8006 (configurable in `.env`)

## Future Enhancements

- Add duplicate detection (avoid summarizing same page twice)
- Add summary expiration (delete old summaries after X days)
- Add summary categories (flights, hotels, activities, etc.)
- Add summary search/filtering
- Add manual summary deletion from UI
- Add summary export/import functionality

