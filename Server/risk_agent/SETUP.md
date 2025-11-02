# Risk Agent MCP Server - Quick Setup Guide

## Overview

This MCP server provides tools for the risk agent to assess travel risks. It exposes 6 tools:

1. Weather forecasting
2. Severe weather detection
3. Natural disaster alerts (GDACS)
4. Web search for risks (Tavily)
5. Comprehensive risk search
6. Travel advisories

## Quick Start

### 1. Verify Dependencies

Ensure you have all required packages:

```bash
pip install fastmcp tavily-python requests python-dotenv python-dateutil
```

### 2. Set API Keys

Create or update `.env` in the project root:

```env
OPENWEATHER_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
GDACS_ENABLED=true
```

### 3. Configure MCP Server

Edit `~/.cursor/mcp.json` (or create it if it doesn't exist):

```json
{
  "mcpServers": {
    "RiskAgentServer": {
      "command": "python",
      "args": ["-m", "risk_agent.mcp_server"],
      "cwd": "C:\\Users\\Sean\\Documents\\CS Projects\\singhacks"
    }
  }
}
```

**Important:** 
- Replace the `cwd` path with your actual project directory path
- On Windows, use backslashes (`\\`) or forward slashes (`/`) for the path
- If using a virtual environment, use the full path to the venv's Python executable in `command`

### 4. Restart Cursor

After updating `mcp.json`, restart Cursor to load the MCP server.

### 5. Test the Server

You can test if the server is working by asking Cursor's AI assistant to:
- "Check weather forecast for Tokyo, Japan"
- "Search for travel risks in Paris, France"

The AI should be able to use the MCP tools automatically.

## Troubleshooting

### Server Won't Start

1. **Check Python path**: Verify the `command` in `mcp.json` points to the correct Python executable
2. **Check module path**: Ensure `risk_agent` is importable (should be in the project root)
3. **Check dependencies**: Run `pip list | grep fastmcp` to verify FastMCP is installed
4. **Check logs**: Look for error messages in Cursor's output/logs

### API Errors

1. **Verify API keys**: Check `.env` file has correct keys
2. **Test API keys manually**: Try calling the APIs directly to verify they work
3. **Check rate limits**: Some APIs have rate limits

### Tools Not Available

1. **Restart Cursor**: MCP servers are loaded on startup
2. **Check server name**: Ensure "RiskAgentServer" matches in `mcp.json`
3. **Verify server running**: Check if the server process is running

## Manual Testing

You can test tools programmatically:

```python
python -m risk_agent.example_usage
```

This will run example usage of all tools.

## Next Steps

- Use the tools in your risk agent code
- Integrate with your existing risk assessment pipeline
- Add additional tools as needed (see README.md for suggestions)

