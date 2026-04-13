# Summary Agent - Quick Start

## What is Summary Agent?

The Summary Agent extracts key information from travel-related pages you browse and provides that context to the Master Agent for personalized insurance recommendations.

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd Server/summary_agent
pip install -r requirements.txt
```

### 2. Set API Key

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_api_key_here"

# Windows CMD
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

### 3. Start Server

```bash
cd Server
python start_summary_agent.py
```

### 4. Verify Server

Open browser: `http://localhost:8020/health`

Should see:
```json
{
  "status": "healthy",
  "service": "Summary Agent API",
  "version": "1.0.0"
}
```

## How It Works

1. **Browse travel pages** (flights, hotels, tours)
2. **Decision Agent detects** travel content
3. **Summary Agent extracts** key details automatically
4. **Master Agent uses** summaries for personalized recommendations

## Testing

### Browse a travel site
- Example: skyscanner.com, booking.com, expedia.com

### Check browser console
Should see:
```
📊 Character count sent to Decision Agent: 8523 characters
📝 Calling Summary Agent for page summary...
✅ Summary generated successfully
📦 Stored page summary in localStorage
```

### Open chatbot
Ask: "What insurance do I need?"

Master Agent should reference your browsing history!

## Configuration

Create `.env` file in `Server/` directory:

```bash
OPENAI_API_KEY=your_api_key_here
SUMMARY_AGENT_PORT=8020
SUMMARY_TEMPERATURE=0.3
SUMMARY_MAX_TOKENS=300
```

## Troubleshooting

### Server won't start
- Check OpenAI API key is set
- Check port 8020 is not in use
- Check dependencies are installed

### Summaries not generated
- Check Decision Agent is running (port 8004)
- Check browser console for errors
- Verify Summary Agent server is healthy

### Master Agent doesn't use summaries
- Check sidepanel console: `[Page Summaries] Loaded from localStorage`
- Check Master Agent logs: `🌐 Page summaries available`
- Verify Master Agent is running (port 9000)

## Port Configuration

- **Summary Agent**: 8020
- **Decision Agent**: 8004
- **Master Agent**: 9000

## Learn More

See `SUMMARY_AGENT_INTEGRATION.md` for complete documentation.

